#!/usr/bin/env python3
r"""Analyse the FHOPS 1.0.1 rolling-horizon re-run and generate every result asset of the paper.

Reads the per-run outputs of ``scripts/rolling_rerun_v101.py`` in the experiment repository
(``UBC-FRESH/jaffray-masc-fhops-model``): ``runs/<run_id>.json`` and
``runs/<run_id>_assignments.csv``. Each stitched plan is replayed against its full scenario with
FHOPS deterministic playback, so every metric comes from the implemented schedule.

Per-run metrics (``results/rerun/runs_metrics.csv``)
---------------------------------------------------
- ``delivered_m3`` / ``remaining_m3``: playback KPIs (``total_production``,
  ``remaining_work_total``).
- ``rel_baseline``: delivered / delivered of the same-method full-horizon baseline of the scenario.
- ``rel_best``: delivered / the largest delivered volume of any run (either method, any
  configuration, baselines included) for the scenario ("best known plan").
- ``violations``: ``sequencing_violation_count`` of the replayed plan.
- ``violations_material``: the same count from a replay with a volume tolerance of ``TINY_M3``
  (1e-3 m3) instead of FHOPS's 1e-6 m3, so violations caused by negligible-production rows
  (numerical artefacts, UBC-FRESH/fhops#157) are not counted. ``tiny_rows`` counts MIP assignment
  rows with planned production below ``TINY_M3``.
- ``moves``: block-to-block machine moves between consecutive working slots of each machine,
  counted on playback records that produced volume (> 1e-6 m3).
- ``continuity``: for every block and pair of consecutive working days, the share of the machines
  working the block on the first day that also work it on the next; pooled over blocks and days
  (sum of intersections / sum of first-day machine counts).
- Window outcomes: windows, stage-1 and earliness time-limit hits, ``no_solution``, ``skipped``,
  ``empty``; ``solve_time_s`` (sum of window runtimes) and ``wall_time_s``.

Generated assets
----------------
- ``results/rerun/runs_metrics.csv`` (+ ``results/rerun/summary.csv`` copied from the
  run directory).
- ``manuscript/tables/baselines.tex``, ``manuscript/tables/window_outcomes.tex``.
- ``manuscript/figures/fig_delivered.pdf``, ``manuscript/figures/fig_effort.pdf``.
- ``manuscript/generated/numbers.tex``: ``\\newcommand`` macros for numbers quoted in the text.
- ``results/rerun/gurobi_work_rates.csv``: work units per second of every Gurobi solve > 100 s
  (from the per-run solver logs), used to report the effective solver effort.

Usage
-----
    python scripts/analyze_rerun.py --rerun-dir \\
        ../jaffray-masc-fhops-model/data/output/rerun_v101_gurobi
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
from concurrent.futures import ProcessPoolExecutor
from itertools import pairwise
from pathlib import Path
from typing import Any, Protocol, TypedDict, cast

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TINY_M3 = 1e-3
WORK_EPS = 1e-6
AREAS = {"ni": "North Island", "ka": "Kamloops", "pg": "Prince George"}
SIZES = [6, 18, 40]
LOCKS = [1, 7, 14]
THETAS = [2, 4, 8, 16]
FULL_X = 2**4.6  # x position of the full-horizon baselines in fig_delivered
WORDS = {1: "One", 6: "Six", 7: "Seven", 14: "Fourteen", 18: "Eighteen", 40: "Forty"}
METHOD_LABEL = {"sa": "SA", "mip": "MIP"}


class Iteration(TypedDict, total=False):
    """One rolling-horizon window record, with the fields the analysis reads."""

    warnings: list[str]
    status: str
    empty: bool
    runtime_s: float


class RunSpec(TypedDict):
    """The ``spec`` block of a run JSON, with the fields the analysis reads."""

    baseline: bool
    solver: str
    context: str
    size: str
    sub_days: int
    lock_days: int
    master_days: int
    theta_weeks: int | None
    mip_time_limit: int
    mip_earliness_time_limit: int | None
    mip_solver: str | None


class PlaybackRecordLike(Protocol):
    """The playback-record fields that ``_moves_and_continuity`` reads."""

    block_id: str | None
    production_units: float | None
    machine_id: str
    day: int
    shift_id: str


class RunMetricsRow(TypedDict, total=False):
    """One per-run metrics row, before the relative columns are added."""

    run_id: str
    context: str
    size: int
    method: str
    mip_solver: str | None
    baseline: bool
    theta_weeks: int | None
    sub_days: int
    lock_days: int
    master_days: int
    mip_time_limit_s: int
    mip_earliness_time_limit_s: int | None
    fhops_version: str | None
    wall_time_s: float
    n_locked_assignments: int | None
    windows: int
    windows_stage1_time_limit: int
    windows_earliness_time_limit: int
    windows_no_solution: int
    windows_skipped: int
    windows_empty: int
    solve_time_s: float
    delivered_m3: float
    remaining_m3: float
    completed_blocks: int | None
    violations: int | None
    total_volume_m3: float
    tiny_rows: int
    violations_material: int
    moves: int
    continuity: float


# ----------------------------------------------------------------------------- per-run metrics
def _window_outcomes(iterations: list[Iteration]) -> dict[str, int | float]:
    stage1_tl = early_tl = 0
    for it in iterations:
        warnings = it.get("warnings") or []
        if any(w == "termination_condition=maxTimeLimit" for w in warnings):
            stage1_tl += 1
        if any(w.startswith("earliness=") and "maxTimeLimit" in w for w in warnings):
            early_tl += 1
    return {
        "windows": len(iterations),
        "windows_stage1_time_limit": stage1_tl,
        "windows_earliness_time_limit": early_tl,
        "windows_no_solution": sum(it.get("status") == "no_solution" for it in iterations),
        "windows_skipped": sum(it.get("status") == "skipped" for it in iterations),
        "windows_empty": sum(bool(it.get("empty")) for it in iterations),
        "solve_time_s": sum(float(it.get("runtime_s") or 0.0) for it in iterations),
    }


def _moves_and_continuity(
    records: list[PlaybackRecordLike], shift_order: dict[str, int]
) -> tuple[int, float]:
    working = [r for r in records if r.block_id and (r.production_units or 0.0) > WORK_EPS]
    by_machine: dict[str, list[tuple[int, int, str]]] = {}
    for r in working:
        block = cast(str, r.block_id)
        by_machine.setdefault(r.machine_id, []).append(
            (r.day, shift_order.get(r.shift_id, 0), block)
        )
    moves = 0
    for slots in by_machine.values():
        slots.sort()
        moves += sum(1 for a, b in pairwise(slots) if a[2] != b[2])
    by_block: dict[str, dict[int, set[str]]] = {}
    for r in working:
        by_block.setdefault(cast(str, r.block_id), {}).setdefault(r.day, set()).add(r.machine_id)
    kept = total = 0
    for days in by_block.values():
        ordered = sorted(days)
        for d0, d1 in pairwise(ordered):
            kept += len(days[d0] & days[d1])
            total += len(days[d0])
    return moves, (kept / total if total else math.nan)


def material_violations(problem: Any, assignments: pd.DataFrame) -> int:  # noqa: ANN401 - fhops is untyped
    """Count sequencing violations with a volume tolerance of ``TINY_M3``.

    FHOPS playback compares volumes with ``fhops.evaluation.sequencing.SEQUENCING_TOLERANCE``
    (read at call time). Raising it to ``TINY_M3`` for one replay treats proposals of at most
    ``TINY_M3`` as idle and ignores shortfalls of at most ``TINY_M3``, so only violations of
    material volume are counted.

    Parameters
    ----------
    problem : Any
        The FHOPS problem for the scenario (untyped library).
    assignments : pandas.DataFrame
        The stitched assignment rows to replay.

    Returns
    -------
    int
        The number of sequencing violations at the ``TINY_M3`` tolerance.
    """
    import fhops.evaluation.sequencing as seq
    from fhops.evaluation.metrics.kpis import compute_kpis

    saved = seq.SEQUENCING_TOLERANCE
    seq.SEQUENCING_TOLERANCE = TINY_M3
    try:
        return int(compute_kpis(problem, assignments)["sequencing_violation_count"])
    finally:
        seq.SEQUENCING_TOLERANCE = saved


def run_metrics(args: tuple[str, str, str]) -> dict[str, Any]:
    """Compute the per-run metrics for one run by replaying its stitched assignments.

    Parameters
    ----------
    args : tuple of str
        The run JSON path, the assignments CSV path, and the scenario YAML path.

    Returns
    -------
    dict of str to Any
        The run's identifiers, window outcomes, delivered and remaining volume, violations,
        moves, and continuity.
    """
    json_path, assignments_path, scenario_path = args
    from fhops.evaluation.playback import run_playback
    from fhops.scenario.contract import Problem
    from fhops.scenario.io import load_scenario

    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    spec = data["spec"]
    row = {
        "run_id": data["run_id"],
        "context": spec["context"],
        "size": int(spec["size"]),
        "method": spec["solver"],
        "mip_solver": spec.get("mip_solver") if spec["solver"] == "mip" else None,
        "baseline": bool(spec["baseline"]),
        "theta_weeks": spec["theta_weeks"],
        "sub_days": spec["sub_days"],
        "lock_days": spec["lock_days"],
        "master_days": spec["master_days"],
        "mip_time_limit_s": spec["mip_time_limit"],
        "mip_earliness_time_limit_s": spec.get("mip_earliness_time_limit"),
        "fhops_version": data.get("provenance", {}).get("fhops_version"),
        "wall_time_s": data["wall_time_s"],
        "n_locked_assignments": data.get("n_locked_assignments"),
    }
    row.update(_window_outcomes(data["plan_summary"].get("iterations", [])))
    kpis = data["kpis"]
    row["delivered_m3"] = kpis["total_production"]
    row["remaining_m3"] = kpis["remaining_work_total"]
    row["completed_blocks"] = kpis.get("completed_blocks")
    row["violations"] = kpis.get("sequencing_violation_count")

    scenario = load_scenario(scenario_path)
    problem = Problem.from_scenario(scenario)
    assignments = pd.read_csv(assignments_path)
    row["total_volume_m3"] = float(sum(b.work_required for b in scenario.blocks))
    row["tiny_rows"] = (
        int((assignments["production"].fillna(0.0) < TINY_M3).sum())
        if "production" in assignments.columns
        else 0
    )
    row["violations_material"] = (
        material_violations(problem, assignments) if len(assignments) else 0
    )
    shift_order = (
        {s.name: i for i, s in enumerate(scenario.timeline.shifts)} if scenario.timeline else {}
    )
    records = run_playback(problem, assignments).records if len(assignments) else []
    row["moves"], row["continuity"] = _moves_and_continuity(records, shift_order)
    return row


def _spec(json_path: Path) -> RunSpec:
    return cast(RunSpec, json.loads(json_path.read_text(encoding="utf-8"))["spec"])


def add_relatives(df: pd.DataFrame) -> pd.DataFrame:
    """Add ``rel_best``, ``rel_baseline`` and ``share_of_volume`` to a paper-set frame.

    Parameters
    ----------
    df : pandas.DataFrame
        The paper-set metrics, with ``context``, ``size``, ``method``, ``baseline``,
        ``delivered_m3`` and ``total_volume_m3`` columns. Modified in place.

    Returns
    -------
    pandas.DataFrame
        The same frame with the relative columns added.
    """
    key = ["context", "size"]
    best = df.groupby(key)["delivered_m3"].transform("max")
    df["rel_best"] = df["delivered_m3"] / best.where(best > 0)
    base = df[df.baseline].set_index([*key, "method"])["delivered_m3"]
    df["baseline_delivered_m3"] = [
        base.get((c, s, m), math.nan)
        for c, s, m in zip(df.context, df["size"], df.method, strict=False)
    ]
    df["rel_baseline"] = df["delivered_m3"] / df["baseline_delivered_m3"].where(
        df["baseline_delivered_m3"] > 0
    )
    df["share_of_volume"] = df["delivered_m3"] / df["total_volume_m3"]
    return df


def collect(
    main_dir: Path, override_dirs: list[Path], model_repo: Path, workers: int, methods: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute metrics for every selected run.

    The main grid directory supplies every run. A full-horizon MIP baseline that also exists in an
    override directory (the 7200 s re-runs) is replaced by the override in the paper set; the grid
    record is kept as ``superseded`` for the supplementary table.

    Parameters
    ----------
    main_dir : pathlib.Path
        The grid directory with the ``runs/`` subdirectory.
    override_dirs : list of pathlib.Path
        Directories whose full-horizon MIP baselines replace the grid's.
    model_repo : pathlib.Path
        The experiment repository with the scenario bundles.
    workers : int
        Concurrent processes for the replay.
    methods : {"both", "sa", "mip"}
        Which solver results to include.

    Returns
    -------
    tuple of pandas.DataFrame
        The paper set with the relative columns, and the superseded grid baselines.
    """
    entries: list[tuple[Path, str, bool]] = []  # (json, source, in_paper_set)
    overrides: set[str] = set()
    for d in override_dirs:
        if not (d / "runs").exists():
            continue
        for jp in sorted((d / "runs").glob("*.json")):
            sp = _spec(jp)
            if sp["baseline"] and sp["solver"] == "mip" and methods in ("both", "mip"):
                overrides.add(jp.stem)
                entries.append((jp, d.name, True))
    for jp in sorted((main_dir / "runs").glob("*.json")):
        sp = _spec(jp)
        if methods not in ("both", sp["solver"]):
            continue
        is_superseded = jp.stem in overrides and sp["baseline"]
        entries.append((jp, main_dir.name, not is_superseded))
    jobs = []
    for jp, _source, _paper in entries:
        sp = _spec(jp)
        sc = (
            model_repo
            / "data"
            / "input"
            / "scenarios"
            / f"{sp['context']}_{sp['size']}"
            / "scenario.yaml"
        )
        jobs.append((str(jp), str(jp.with_name(f"{jp.stem}_assignments.csv")), str(sc)))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(run_metrics, jobs))
    for row, (_, source, in_paper) in zip(rows, entries, strict=False):
        row["source"] = source
        row["paper_set"] = in_paper
    df = pd.DataFrame(rows)
    paper_df = add_relatives(df[df.paper_set].copy())
    superseded_df = df[~df.paper_set].copy()
    order = ["method", "size", "context", "baseline", "sub_days", "lock_days"]
    return paper_df.sort_values(order).reset_index(drop=True), superseded_df.sort_values(
        order
    ).reset_index(drop=True)


# ----------------------------------------------------------------------------- solver logs
def gurobi_work_rates(rerun_dir: Path, min_seconds: float = 100.0) -> pd.DataFrame:
    """Compute work units per second for every Gurobi solve over ``min_seconds``.

    Each ``runs/<run_id>.gurobi.log`` holds both stages of every window; the final line of each
    solve reads "Explored ... in S seconds (W work units)". Short solves are excluded because their
    rate is dominated by start-up overhead.

    Parameters
    ----------
    rerun_dir : pathlib.Path
        The run directory with the ``runs/`` subdirectory of Gurobi logs.
    min_seconds : float, optional
        Exclude solves at or below this many seconds. The default is 100.

    Returns
    -------
    pandas.DataFrame
        One row per solve, with ``run_id``, ``seconds``, ``work_units`` and ``work_per_s``.
    """
    import re

    pattern = re.compile(r"Explored .* in ([\d.]+) seconds \(([\d.]+) work units\)")
    rows: list[dict[str, str | float]] = []
    for log in sorted((rerun_dir / "runs").glob("*.gurobi.log")):
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            m = pattern.search(line)
            if m and float(m.group(1)) > min_seconds:
                rows.append(
                    {
                        "run_id": log.name.removesuffix(".gurobi.log"),
                        "seconds": float(m.group(1)),
                        "work_units": float(m.group(2)),
                    }
                )
    df = pd.DataFrame(rows, columns=["run_id", "seconds", "work_units"])
    df["work_per_s"] = df["work_units"] / df["seconds"]
    return df


# ----------------------------------------------------------------------------- tables
def _fmt(x: float | None, nd: int = 1) -> str:
    return "--" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:,.{nd}f}"


def table_baselines(df: pd.DataFrame, out: Path) -> None:
    """Write the full-horizon baseline table (Table 2) to ``out``.

    Parameters
    ----------
    df : pandas.DataFrame
        The paper-set metrics, with ``baseline``, ``context``, ``size``, ``method``,
        ``share_of_volume`` and ``wall_time_s`` columns.
    out : pathlib.Path
        The LaTeX file to write.
    """
    b = df[df.baseline]
    lines = [
        "% Generated by scripts/analyze_rerun.py; do not edit.",
        "\\begin{tabular}{lrrrrr}",
        "\\toprule",
        " & & \\multicolumn{2}{c}{Delivered (\\% of volume)} & "
        "\\multicolumn{2}{c}{Wall time (h)} \\\\",
        "\\cmidrule(lr){3-4}\\cmidrule(lr){5-6}",
        "Study area & Blocks & SA & MIP & SA & MIP \\\\",
        "\\midrule",
    ]
    for ctx, name in AREAS.items():
        for size in SIZES:
            sa = b[(b.context == ctx) & (b["size"] == size) & (b.method == "sa")]
            mip = b[(b.context == ctx) & (b["size"] == size) & (b.method == "mip")]
            if sa.empty and mip.empty:
                continue

            def cell(d: pd.DataFrame, c: str, k: float = 1.0) -> float | None:
                return float(d[c].iloc[0]) * k if not d.empty else None

            lines.append(
                f"{name} & {size} & {_fmt(cell(sa, 'share_of_volume', 100))} & "
                f"{_fmt(cell(mip, 'share_of_volume', 100))} & "
                f"{_fmt(cell(sa, 'wall_time_s', 1 / 3600), 2)} & "
                f"{_fmt(cell(mip, 'wall_time_s', 1 / 3600), 2)} \\"
            )
    lines += ["\\bottomrule", "\\end{tabular}"]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def table_window_outcomes(df: pd.DataFrame, out: Path) -> None:
    """Write the window-outcomes table (Table 3) to ``out``.

    Parameters
    ----------
    df : pandas.DataFrame
        The paper-set metrics, with ``baseline``, ``method``, ``size`` and the window-outcome
        columns.
    out : pathlib.Path
        The LaTeX file to write.
    """
    r = df[~df.baseline]
    lines = [
        "% Generated by scripts/analyze_rerun.py; do not edit.",
        "\\begin{tabular}{llrrrrr}",
        "\\toprule",
        "Method & Blocks & Windows & Stage-1 limit (\\%) & Earliness limit (\\%) & "
        "No solution & Empty \\\\",
        "\\midrule",
    ]
    for method in ["mip", "sa"]:
        for size in SIZES:
            g = r[(r.method == method) & (r["size"] == size)]
            if g.empty:
                continue
            n = int(g.windows.sum())

            def pct(c: str, group: pd.DataFrame = g, total: int = n) -> float | None:
                return 100 * float(group[c].sum()) / total if total else None

            stage1 = _fmt(pct("windows_stage1_time_limit")) if method == "mip" else "--"
            early = _fmt(pct("windows_earliness_time_limit")) if method == "mip" else "--"
            lines.append(
                f"{METHOD_LABEL[method]} & {size} & {n:,} & {stage1} & {early} & "
                f"{int(g.windows_no_solution.sum())} & {int(g.windows_empty.sum())} \\\\"
            )
    lines += ["\\bottomrule", "\\end{tabular}"]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------- figures
def fig_delivered(df: pd.DataFrame, out: Path) -> None:
    """Write the delivered-volume figure (Fig. 2) to ``out``.

    Parameters
    ----------
    df : pandas.DataFrame
        The paper-set metrics, with ``method``, ``size``, ``baseline``, ``lock_days``,
        ``theta_weeks``, ``context`` and ``rel_best`` columns.
    out : pathlib.Path
        The PDF file to write.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter

    colors = {1: "#1b9e77", 7: "#d95f02", 14: "#7570b3"}
    markers = {"ni": "o", "ka": "s", "pg": "^"}
    fig, axes = plt.subplots(2, 3, figsize=(7.2, 4.8), sharex=True, sharey=True)
    for i, method in enumerate(["sa", "mip"]):
        for j, size in enumerate(SIZES):
            ax = axes[i, j]
            g = df[(df.method == method) & (df["size"] == size)]
            for lock in LOCKS:
                h = g[(~g.baseline) & (g.lock_days == lock)]
                if h.empty:
                    continue
                med = h.groupby("theta_weeks")["rel_best"].median()
                ax.plot(med.index, med.values, color=colors[lock], lw=1.2, label=f"$f$ = {lock} d")
                for ctx, mk in markers.items():
                    hc = h[h.context == ctx]
                    ax.scatter(
                        hc.theta_weeks,
                        hc.rel_best,
                        color=colors[lock],
                        marker=mk,
                        s=12,
                        alpha=0.7,
                        lw=0,
                    )
            base = g[g.baseline]
            for ctx, mk in markers.items():
                bc = base[base.context == ctx]
                ax.scatter(
                    [FULL_X] * len(bc),
                    bc.rel_best,
                    facecolor="none",
                    edgecolor="k",
                    marker=mk,
                    s=40,
                    lw=0.8,
                )
            ax.set_xscale("log", base=2)
            ax.set_xticks([*THETAS, FULL_X], [str(t) for t in THETAS] + ["full"])
            ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
            ax.set_title(f"{METHOD_LABEL[method]}, {size} blocks", fontsize=9)
            ax.grid(alpha=0.3, lw=0.5)
            if j == 0:
                ax.set_ylabel("Delivered / best known")
            if i == 1:
                ax.set_xlabel(r"Planning horizon $\theta$ (weeks)")
    from matplotlib.lines import Line2D

    handles = [
        Line2D([], [], color=colors[lock], lw=1.2, label=f"$f$ = {lock} d") for lock in LOCKS
    ]
    handles += [
        Line2D([], [], color="k", marker=m, ls="", ms=4, label=AREAS[c]) for c, m in markers.items()
    ]
    handles += [
        Line2D([], [], color="k", marker="o", mfc="none", ls="", ms=6, label="Full horizon")
    ]
    fig.legend(handles=handles, loc="lower center", ncol=7, fontsize=7, frameon=False)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(out)
    plt.close(fig)


def fig_effort(df: pd.DataFrame, out: Path) -> None:
    """Write the effort figure (Fig. 3) to ``out``.

    Parameters
    ----------
    df : pandas.DataFrame
        The paper-set metrics, with ``baseline``, ``method``, ``lock_days``, ``wall_time_s``,
        ``continuity`` and ``rel_best`` columns.
    out : pathlib.Path
        The PDF file to write.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = {1: "#1b9e77", 7: "#d95f02", 14: "#7570b3"}
    r = df[~df.baseline]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
    for method, mk in [("sa", "o"), ("mip", "s")]:
        for lock in LOCKS:
            h = r[(r.method == method) & (r.lock_days == lock)]
            axes[0].scatter(
                h.wall_time_s / 3600,
                h.rel_best,
                color=colors[lock],
                marker=mk,
                s=12,
                alpha=0.7,
                lw=0,
            )
            axes[1].scatter(
                h.continuity, h.rel_best, color=colors[lock], marker=mk, s=12, alpha=0.7, lw=0
            )
    from matplotlib.ticker import PercentFormatter

    axes[0].set_xscale("log")
    axes[0].set_xlabel("Wall time per run (h)")
    axes[1].set_xlabel("Schedule continuity")
    for ax, tag in zip(axes, "ab", strict=False):
        ax.set_ylabel("Delivered / best known")
        ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
        ax.grid(alpha=0.3, lw=0.5)
        ax.set_title(f"({tag})", loc="left", fontsize=9)
    from matplotlib.lines import Line2D

    handles = [
        Line2D([], [], color=c, marker="o", ls="", ms=4, label=f"$f$ = {k} d")
        for k, c in colors.items()
    ]
    handles += [
        Line2D([], [], color="k", marker=m, ls="", ms=4, label=lab)
        for m, lab in [("o", "SA"), ("s", "MIP")]
    ]
    fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=7, frameon=False)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(out)
    plt.close(fig)


# ----------------------------------------------------------------------------- numbers
def numbers(df: pd.DataFrame, out: Path, rates: pd.DataFrame | None = None) -> None:
    r"""Write the ``\\newcommand`` macros quoted in the text to ``out``.

    Parameters
    ----------
    df : pandas.DataFrame
        The paper-set metrics.
    out : pathlib.Path
        The LaTeX file to write.
    rates : pandas.DataFrame or None
        The Gurobi work-rate table, or ``None`` to omit the work-rate macros.
    """
    r = df[~df.baseline]
    macros: dict[str, str] = {
        "NRuns": f"{len(df)}",
        "NRollingRuns": f"{len(r)}",
        "NBaselineRuns": f"{int(df.baseline.sum())}",
        "NWindows": f"{int(r.windows.sum()):,}",
        "NWindowsNoSolution": f"{int(df.windows_no_solution.sum())}",
        "NWindowsEmpty": f"{int(df.windows_empty.sum())}",
        "NRunsWithViolations": f"{int((df.violations > 0).sum())}",
        "NRunsWithMaterialViolations": f"{int((df.violations_material > 0).sum())}",
        "TinyThreshold": f"{TINY_M3:g}",
    }
    for method in ["sa", "mip"]:
        m = METHOD_LABEL[method]
        for lock in LOCKS:
            h = r[(r.method == method) & (r.lock_days == lock)]
            if not h.empty:
                macros[f"RelBestMedian{m}Lock{WORDS[lock]}"] = f"{100 * h.rel_best.median():.1f}"
                macros[f"RelBestMin{m}Lock{WORDS[lock]}"] = f"{100 * h.rel_best.min():.1f}"
        for size in SIZES:
            h = r[(r.method == method) & (r["size"] == size)]
            if not h.empty:
                macros[f"WallMedianHours{m}{WORDS[size]}"] = f"{h.wall_time_s.median() / 3600:.2f}"
    if rates is not None and not rates.empty:
        macros["GurobiWorkRateMedian"] = f"{rates.work_per_s.median():.2f}"
        macros["GurobiWorkRateLow"] = f"{rates.work_per_s.quantile(0.05):.2f}"
        macros["GurobiWorkRateHigh"] = f"{rates.work_per_s.quantile(0.95):.2f}"
        macros["GurobiSolvesLogged"] = f"{len(rates):,}"
    lines = ["% Generated by scripts/analyze_rerun.py; do not edit."]
    lines += [f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in sorted(macros.items())]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Run the analysis end to end and write every result asset.

    Returns
    -------
    int
        0 on success.
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    out = ROOT.parent / "jaffray-masc-fhops-model" / "data" / "output"
    parser.add_argument(
        "--rerun-dir", type=Path, default=out / "rerun_v101_gurobi", help="main grid directory"
    )
    parser.add_argument(
        "--baseline-dir",
        type=Path,
        action="append",
        default=None,
        help="directory of full-horizon MIP baselines that replace the grid's (repeatable)",
    )
    parser.add_argument("--model-repo", type=Path, default=ROOT.parent / "jaffray-masc-fhops-model")
    parser.add_argument("--methods", choices=["both", "sa", "mip"], default="both")
    parser.add_argument(
        "--out-tag", default="rerun", help="results/<tag>/ and asset suffix ('rerun' for the paper)"
    )
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    if args.baseline_dir is None:
        args.baseline_dir = [
            out / "rerun_v101_gurobi_sensitivity_ni40_baseline_7200s",
            out / "rerun_v101_gurobi_sensitivity_size40_baselines_7200s",
        ]

    res = ROOT / "results" / args.out_tag
    res.mkdir(parents=True, exist_ok=True)
    df, superseded = collect(
        args.rerun_dir, args.baseline_dir, args.model_repo, args.workers, args.methods
    )
    df.to_csv(res / "runs_metrics.csv", index=False)
    if not superseded.empty:
        superseded.to_csv(res / "supplementary_baselines_grid_1800s.csv", index=False)
    if args.methods == "both" and (args.rerun_dir / "summary.csv").exists():
        shutil.copy2(args.rerun_dir / "summary.csv", res / "summary.csv")
    suffix = "" if args.out_tag == "rerun" else f"_{args.out_tag}"
    tables = ROOT / "manuscript" / "tables"
    figures = ROOT / "manuscript" / "figures"
    generated = ROOT / "manuscript" / "generated"
    for d in (tables, figures, generated):
        d.mkdir(parents=True, exist_ok=True)
    table_baselines(df, tables / f"baselines{suffix}.tex")
    table_window_outcomes(df, tables / f"window_outcomes{suffix}.tex")
    fig_delivered(df, figures / f"fig_delivered{suffix}.pdf")
    fig_effort(df, figures / f"fig_effort{suffix}.pdf")
    rates = gurobi_work_rates(args.rerun_dir)
    rates.to_csv(res / "gurobi_work_rates.csv", index=False)
    numbers(df, generated / f"numbers{suffix}.tex", rates)
    cols = [
        "run_id",
        "source",
        "delivered_m3",
        "rel_baseline",
        "rel_best",
        "violations",
        "violations_material",
        "moves",
        "continuity",
    ]
    print(df[cols].round(3).to_string(index=False))
    if not superseded.empty:
        print("\nSuperseded grid baselines (1800 s, supplementary):")
        print(superseded[["run_id", "delivered_m3"]].round(0).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
