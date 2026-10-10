#!/usr/bin/env python3
"""Analyse the FHOPS 1.0.1 rolling-horizon re-run and generate every result asset of the paper.

Reads the per-run outputs of ``scripts/rolling_rerun_v101.py`` in the experiment repository
(``UBC-FRESH/jaffray-masc-fhops-model``): ``runs/<run_id>.json`` and
``runs/<run_id>_assignments.csv``. Each stitched plan is replayed against its full scenario with
FHOPS deterministic playback, so every metric comes from the implemented schedule.

Per-run metrics (``results/rerun/runs_metrics.csv``)
---------------------------------------------------
- ``delivered_m3`` / ``remaining_m3``: playback KPIs (``total_production``, ``remaining_work_total``).
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
- ``results/rerun/runs_metrics.csv`` (+ ``results/rerun/summary.csv`` copied from the run directory).
- ``manuscript/tables/baselines.tex``, ``manuscript/tables/window_outcomes.tex``.
- ``manuscript/figures/fig_delivered.pdf``, ``manuscript/figures/fig_effort.pdf``.
- ``manuscript/generated/numbers.tex``: ``\\newcommand`` macros for numbers quoted in the text.

Usage
-----
    python scripts/analyze_rerun.py --rerun-dir ../jaffray-masc-fhops-model/data/output/rerun_v101_gurobi
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

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


# ----------------------------------------------------------------------------- per-run metrics
def _window_outcomes(iterations: list[dict]) -> dict:
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


def _moves_and_continuity(records, shift_order: dict[str, int]) -> tuple[int, float]:
    working = [r for r in records if r.block_id and (r.production_units or 0.0) > WORK_EPS]
    by_machine: dict[str, list] = {}
    for r in working:
        by_machine.setdefault(r.machine_id, []).append((r.day, shift_order.get(r.shift_id, 0), r.block_id))
    moves = 0
    for slots in by_machine.values():
        slots.sort()
        moves += sum(1 for a, b in zip(slots, slots[1:]) if a[2] != b[2])
    by_block: dict[str, dict[int, set]] = {}
    for r in working:
        by_block.setdefault(r.block_id, {}).setdefault(r.day, set()).add(r.machine_id)
    kept = total = 0
    for days in by_block.values():
        ordered = sorted(days)
        for d0, d1 in zip(ordered, ordered[1:]):
            kept += len(days[d0] & days[d1])
            total += len(days[d0])
    return moves, (kept / total if total else math.nan)


def material_violations(problem, assignments: pd.DataFrame) -> int:
    """Sequencing violations with a volume tolerance of ``TINY_M3`` instead of FHOPS's 1e-6 m3.

    FHOPS playback compares volumes with ``fhops.evaluation.sequencing.SEQUENCING_TOLERANCE``
    (read at call time). Raising it to ``TINY_M3`` for one replay treats proposals of at most
    ``TINY_M3`` as idle and ignores shortfalls of at most ``TINY_M3``, so only violations of
    material volume are counted.
    """
    import fhops.evaluation.sequencing as seq
    from fhops.evaluation.metrics.kpis import compute_kpis

    saved = seq.SEQUENCING_TOLERANCE
    seq.SEQUENCING_TOLERANCE = TINY_M3
    try:
        return int(compute_kpis(problem, assignments)["sequencing_violation_count"])
    finally:
        seq.SEQUENCING_TOLERANCE = saved


def run_metrics(args: tuple[str, str, str]) -> dict:
    json_path, assignments_path, scenario_path = args
    from fhops.evaluation.metrics.kpis import compute_kpis
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
        int((assignments["production"].fillna(0.0) < TINY_M3).sum()) if "production" in assignments.columns else 0
    )
    row["violations_material"] = material_violations(problem, assignments) if len(assignments) else 0
    shift_order = {s.name: i for i, s in enumerate(scenario.timeline.shifts)} if scenario.timeline else {}
    records = run_playback(problem, assignments).records if len(assignments) else []
    row["moves"], row["continuity"] = _moves_and_continuity(records, shift_order)
    return row


def collect(rerun_dir: Path, model_repo: Path, workers: int) -> pd.DataFrame:
    jobs = []
    for jp in sorted((rerun_dir / "runs").glob("*.json")):
        run_id = jp.stem
        ap = jp.with_name(f"{run_id}_assignments.csv")
        data = json.loads(jp.read_text(encoding="utf-8"))
        ctx, size = data["spec"]["context"], data["spec"]["size"]
        sp = model_repo / "data" / "input" / "scenarios" / f"{ctx}_{size}" / "scenario.yaml"
        jobs.append((str(jp), str(ap), str(sp)))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(run_metrics, jobs))
    df = pd.DataFrame(rows)
    key = ["context", "size"]
    best = df.groupby(key)["delivered_m3"].transform("max")
    df["rel_best"] = df["delivered_m3"] / best.where(best > 0)
    base = df[df.baseline].set_index(key + ["method"])["delivered_m3"]
    df["baseline_delivered_m3"] = [base.get((c, s, m), math.nan) for c, s, m in zip(df.context, df["size"], df.method)]
    df["rel_baseline"] = df["delivered_m3"] / df["baseline_delivered_m3"].where(df["baseline_delivered_m3"] > 0)
    df["share_of_volume"] = df["delivered_m3"] / df["total_volume_m3"]
    return df.sort_values(["method", "size", "context", "baseline", "sub_days", "lock_days"]).reset_index(drop=True)


# ----------------------------------------------------------------------------- tables
def _fmt(x: float, nd: int = 1) -> str:
    return "--" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:,.{nd}f}"


def table_baselines(df: pd.DataFrame, out: Path) -> None:
    b = df[df.baseline]
    lines = [
        "% Generated by scripts/analyze_rerun.py; do not edit.",
        "\\begin{tabular}{lrrrrr}",
        "\\toprule",
        " & & \\multicolumn{2}{c}{Delivered (\\% of volume)} & \\multicolumn{2}{c}{Wall time (h)} \\\\",
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
            g = lambda d, c, k=1.0: d[c].iloc[0] * k if not d.empty else math.nan  # noqa: E731
            lines.append(
                f"{name} & {size} & {_fmt(g(sa, 'share_of_volume', 100))} & {_fmt(g(mip, 'share_of_volume', 100))} & "
                f"{_fmt(g(sa, 'wall_time_s', 1 / 3600), 2)} & {_fmt(g(mip, 'wall_time_s', 1 / 3600), 2)} \\\\"
            )
    lines += ["\\bottomrule", "\\end{tabular}"]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def table_window_outcomes(df: pd.DataFrame, out: Path) -> None:
    r = df[~df.baseline]
    lines = [
        "% Generated by scripts/analyze_rerun.py; do not edit.",
        "\\begin{tabular}{llrrrrr}",
        "\\toprule",
        "Method & Blocks & Windows & Stage-1 limit (\\%) & Earliness limit (\\%) & No solution & Empty \\\\",
        "\\midrule",
    ]
    for method in ["mip", "sa"]:
        for size in SIZES:
            g = r[(r.method == method) & (r["size"] == size)]
            if g.empty:
                continue
            n = int(g.windows.sum())
            pct = lambda c: 100 * g[c].sum() / n if n else math.nan  # noqa: E731
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
                    ax.scatter(hc.theta_weeks, hc.rel_best, color=colors[lock], marker=mk, s=12, alpha=0.7, lw=0)
            base = g[g.baseline]
            for ctx, mk in markers.items():
                bc = base[base.context == ctx]
                ax.scatter([FULL_X] * len(bc), bc.rel_best, facecolor="none", edgecolor="k", marker=mk, s=40, lw=0.8)
            ax.set_xscale("log", base=2)
            ax.set_xticks(THETAS + [FULL_X], [str(t) for t in THETAS] + ["full"])
            ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
            ax.set_title(f"{METHOD_LABEL[method]}, {size} blocks", fontsize=9)
            ax.grid(alpha=0.3, lw=0.5)
            if j == 0:
                ax.set_ylabel("Delivered / best known")
            if i == 1:
                ax.set_xlabel(r"Planning horizon $\theta$ (weeks)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    from matplotlib.lines import Line2D

    handles += [Line2D([], [], color="k", marker=m, ls="", ms=4, label=AREAS[c]) for c, m in markers.items()]
    handles += [Line2D([], [], color="k", marker="o", mfc="none", ls="", ms=6, label="Full horizon")]
    fig.legend(handles=handles, loc="lower center", ncol=7, fontsize=7, frameon=False)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(out)
    plt.close(fig)


def fig_effort(df: pd.DataFrame, out: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = {1: "#1b9e77", 7: "#d95f02", 14: "#7570b3"}
    r = df[~df.baseline]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
    for method, mk in [("sa", "o"), ("mip", "s")]:
        for lock in LOCKS:
            h = r[(r.method == method) & (r.lock_days == lock)]
            axes[0].scatter(h.wall_time_s / 3600, h.rel_best, color=colors[lock], marker=mk, s=12, alpha=0.7, lw=0)
            axes[1].scatter(h.continuity, h.rel_best, color=colors[lock], marker=mk, s=12, alpha=0.7, lw=0)
    from matplotlib.ticker import PercentFormatter

    axes[0].set_xscale("log")
    axes[0].set_xlabel("Wall time per run (h)")
    axes[1].set_xlabel("Schedule continuity")
    for ax, tag in zip(axes, "ab"):
        ax.set_ylabel("Delivered / best known")
        ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
        ax.grid(alpha=0.3, lw=0.5)
        ax.set_title(f"({tag})", loc="left", fontsize=9)
    from matplotlib.lines import Line2D

    handles = [Line2D([], [], color=c, marker="o", ls="", ms=4, label=f"$f$ = {k} d") for k, c in colors.items()]
    handles += [Line2D([], [], color="k", marker=m, ls="", ms=4, label=lab) for m, lab in [("o", "SA"), ("s", "MIP")]]
    fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=7, frameon=False)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(out)
    plt.close(fig)


# ----------------------------------------------------------------------------- numbers
def numbers(df: pd.DataFrame, out: Path) -> None:
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
    lines = ["% Generated by scripts/analyze_rerun.py; do not edit."]
    lines += [f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in sorted(macros.items())]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--rerun-dir", type=Path, default=ROOT.parent / "jaffray-masc-fhops-model" / "data" / "output" / "rerun_v101_gurobi"
    )
    parser.add_argument("--model-repo", type=Path, default=ROOT.parent / "jaffray-masc-fhops-model")
    parser.add_argument("--out-tag", default="rerun", help="results/<tag>/ and asset suffix ('rerun' for the paper)")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    res = ROOT / "results" / args.out_tag
    res.mkdir(parents=True, exist_ok=True)
    df = collect(args.rerun_dir, args.model_repo, args.workers)
    df.to_csv(res / "runs_metrics.csv", index=False)
    if (args.rerun_dir / "summary.csv").exists():
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
    numbers(df, generated / f"numbers{suffix}.tex")
    cols = ["run_id", "delivered_m3", "rel_baseline", "rel_best", "violations", "violations_material", "moves", "continuity"]
    print(df[cols].round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
