#!/usr/bin/env python3
"""Audit every run of the FHOPS 1.0.1 re-run against its own record before analysis.

For each run JSON in the paper set (grid directory plus the 7200 s baseline folders) the audit
checks that the run is what its spec says it is, and that its saved KPIs follow from its
assignments:

- the window count equals ``ceil(master_days / lock_days)`` for rolling runs and 1 for baselines;
- window start days advance by the lock span, and the last window reaches the horizon end;
- ``n_locked_assignments`` equals the row count of the assignments CSV;
- the saved delivered volume equals a fresh deterministic replay of the same assignments;
- no run carries an ``error`` key.

Results are written to ``results/audit/runs_audit.csv``. The script exits 1 if any check fails.

Usage
-----
    python scripts/audit_rerun_inputs.py --workers 4
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT.parent / "jaffray-masc-fhops-model" / "data" / "output"
GRID = OUTPUT / "rerun_v101_gurobi"
BASELINE_DIRS = [
    OUTPUT / "rerun_v101_gurobi_sensitivity_ni40_baseline_7200s",
    OUTPUT / "rerun_v101_gurobi_sensitivity_size40_baselines_7200s",
]
REPLAY_TOLERANCE = 1e-6


def expected_windows(spec: dict[str, object]) -> int:
    """Return the number of windows a run should contain.

    Parameters
    ----------
    spec : dict of str to object
        The ``spec`` block of a run JSON, with ``master_days``, ``lock_days`` and ``baseline``.

    Returns
    -------
    int
        1 for a full-horizon baseline, otherwise ``ceil(master_days / lock_days)``.
    """
    if spec["baseline"]:
        return 1
    return math.ceil(int(spec["master_days"]) / int(spec["lock_days"]))


def audit_one(args: tuple[str, str, str]) -> dict[str, object]:
    """Audit one run and return its findings as a flat row.

    Parameters
    ----------
    args : tuple of str
        The run JSON path, the assignments CSV path, and the scenario YAML path.

    Returns
    -------
    dict of str to object
        One row per run: identifiers, the individual checks, and the failure messages.
    """
    from fhops.evaluation.metrics.kpis import compute_kpis
    from fhops.scenario.contract import Problem
    from fhops.scenario.io import load_scenario

    json_path, assignments_path, scenario_path = args
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    spec = data["spec"]
    failures: list[str] = []
    iterations = data["plan_summary"].get("iterations", [])

    windows_ok = len(iterations) == expected_windows(spec)
    if not windows_ok:
        failures.append(f"windows {len(iterations)} != {expected_windows(spec)}")
    lock = int(spec["lock_days"])
    master = int(spec["master_days"])
    starts_ok = all(it["start_day"] == 1 + i * lock for i, it in enumerate(iterations)) if not spec["baseline"] else True
    if not starts_ok:
        failures.append("window start days do not advance by the lock span")
    last = iterations[-1] if iterations else None
    horizon_ok = last is not None and min(last["start_day"] + lock - 1, master) == master
    if not horizon_ok:
        failures.append("last window does not reach the horizon end")
    error_free = "error" not in data
    if not error_free:
        failures.append(f"run carries an error: {data['error']}")

    assignments = pd.read_csv(assignments_path) if Path(assignments_path).exists() else pd.DataFrame()
    rows_ok = int(data.get("n_locked_assignments") or 0) == len(assignments)
    if not rows_ok:
        failures.append(f"n_locked_assignments {data.get('n_locked_assignments')} != CSV rows {len(assignments)}")

    scenario = load_scenario(scenario_path)
    replay_total = float(compute_kpis(Problem.from_scenario(scenario), assignments)["total_production"]) if len(assignments) else 0.0
    saved_total = float(data["kpis"]["total_production"])
    replay_ok = abs(replay_total - saved_total) <= REPLAY_TOLERANCE * max(1.0, abs(saved_total))
    if not replay_ok:
        failures.append(f"replayed delivered {replay_total:.6f} != saved {saved_total:.6f}")

    return {
        "run_id": data["run_id"],
        "source": Path(json_path).parents[1].name,
        "solver": spec["solver"],
        "baseline": bool(spec["baseline"]),
        "size": spec["size"],
        "context": spec["context"],
        "sub_days": spec["sub_days"],
        "lock_days": spec["lock_days"],
        "mip_time_limit_s": spec["mip_time_limit"],
        "windows": len(iterations),
        "windows_ok": windows_ok,
        "starts_ok": starts_ok,
        "horizon_ok": horizon_ok,
        "error_free": error_free,
        "rows_ok": rows_ok,
        "replay_ok": replay_ok,
        "saved_delivered_m3": saved_total,
        "replay_delivered_m3": replay_total,
        "failures": "; ".join(failures),
        "passed": not failures,
    }


def paper_set() -> list[Path]:
    """Return the run JSON paths of the paper set, with the 7200 s baselines replacing the grid's.

    Returns
    -------
    list of pathlib.Path
        Grid run JSONs, minus the size-40 baselines that the 7200 s folders supersede, plus those
        folders' baseline JSONs.
    """
    override_ids = {p.stem for d in BASELINE_DIRS if (d / "runs").exists() for p in (d / "runs").glob("*_mip.json")}
    paths = [p for p in sorted((GRID / "runs").glob("*.json"))
             if not (p.stem in override_ids and json.loads(p.read_text())["spec"]["baseline"])]
    for d in BASELINE_DIRS:
        if (d / "runs").exists():
            paths += sorted((d / "runs").glob("*.json"))
    return paths


def main() -> int:
    """Run the audit over the paper set and write its findings.

    Returns
    -------
    int
        0 when every run passes, 1 otherwise.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--model-repo", type=Path, default=ROOT.parent / "jaffray-masc-fhops-model")
    args = parser.parse_args()

    jobs = []
    for jp in paper_set():
        spec = json.loads(jp.read_text(encoding="utf-8"))["spec"]
        scenario = args.model_repo / "data" / "input" / "scenarios" / f"{spec['context']}_{spec['size']}" / "scenario.yaml"
        jobs.append((str(jp), str(jp.with_name(f"{jp.stem}_assignments.csv")), str(scenario)))
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(audit_one, jobs))
    df = pd.DataFrame(rows)
    out = ROOT / "results" / "audit"
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "runs_audit.csv", index=False)
    print(f"audited {len(df)} runs: {int(df.passed.sum())} passed, {int((~df.passed).sum())} failed")
    print(df.groupby(["solver", "baseline"])[["windows_ok", "starts_ok", "horizon_ok", "error_free", "rows_ok", "replay_ok"]].sum().to_string())
    failed = df[~df.passed]
    if not failed.empty:
        print(failed[["run_id", "source", "failures"]].to_string(index=False))
    return 0 if failed.empty else 1


if __name__ == "__main__":
    sys.exit(main())
