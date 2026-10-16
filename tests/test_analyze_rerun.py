"""Unit tests for ``scripts.analyze_rerun``.

The pure functions are tested with small fixtures. The generators are tested on a tiny frame and
checked for the values they must produce. The figure functions are smoke-tested to a PDF.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from analyze_rerun import (
    TINY_M3,
    Iteration,
    PlaybackRecordLike,
    _fmt,
    _moves_and_continuity,
    _spec,
    _window_outcomes,
    add_relatives,
    collect,
    fig_delivered,
    fig_effort,
    gurobi_work_rates,
    main,
    material_violations,
    numbers,
    run_metrics,
    table_baselines,
    table_window_outcomes,
)

MODEL_REPO = Path(__file__).resolve().parents[1].parent / "jaffray-masc-fhops-model"
SCENARIO = MODEL_REPO / "data" / "input" / "scenarios" / "ka_6" / "scenario.yaml"

pytestmark = pytest.mark.skipif(not SCENARIO.exists(), reason="model repo not present")


def _rec(machine: str, block: str, day: int, shift: str, prod: float) -> PlaybackRecordLike:
    return SimpleNamespace(
        machine_id=machine, block_id=block, day=day, shift_id=shift, production_units=prod
    )


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "context": ["ka", "ka", "ka", "ka"],
            "size": [6, 6, 6, 6],
            "method": ["mip", "mip", "sa", "sa"],
            "baseline": [True, False, True, False],
            "sub_days": [112, 14, 112, 14],
            "lock_days": [112, 7, 112, 7],
            "theta_weeks": [None, 2, None, 2],
            "delivered_m3": [100.0, 90.0, 95.0, 88.0],
            "total_volume_m3": [100.0, 100.0, 100.0, 100.0],
            "wall_time_s": [3600.0, 1800.0, 900.0, 450.0],
            "windows": [1, 16, 1, 16],
            "windows_stage1_time_limit": [0, 4, 0, 0],
            "windows_earliness_time_limit": [0, 2, 0, 0],
            "windows_no_solution": [0, 0, 0, 0],
            "windows_skipped": [0, 0, 0, 0],
            "windows_empty": [0, 0, 0, 0],
            "violations": [0, 1, 0, 0],
            "violations_material": [0, 0, 0, 0],
            "continuity": [0.5, 0.6, 0.7, 0.8],
            "share_of_volume": [1.0, 0.9, 0.95, 0.88],
            "rel_best": [1.0, 0.9, 0.95, 0.88],
            "rel_baseline": [1.0, 0.9, 1.0, 0.926],
        }
    )


def test_window_outcomes_counts_each_status() -> None:
    iters: list[Iteration] = [
        {
            "warnings": ["termination_condition=maxTimeLimit"],
            "status": "solved",
            "empty": False,
            "runtime_s": 10.0,
        },
        {
            "warnings": ["earliness=applied value=1 termination_condition=maxTimeLimit"],
            "status": "solved",
            "empty": True,
            "runtime_s": 5.0,
        },
        {"warnings": [], "status": "no_solution", "empty": False, "runtime_s": 1.0},
        {"warnings": [], "status": "skipped", "empty": False, "runtime_s": 0.0},
    ]
    out = _window_outcomes(iters)
    assert out["windows"] == 4
    assert out["windows_stage1_time_limit"] == 1
    assert out["windows_earliness_time_limit"] == 1
    assert out["windows_no_solution"] == 1
    assert out["windows_skipped"] == 1
    assert out["windows_empty"] == 1
    assert out["solve_time_s"] == 16.0


def test_window_outcomes_handles_missing_warnings() -> None:
    iters: list[Iteration] = [{"status": "solved", "empty": False, "runtime_s": 3.0}]
    out = _window_outcomes(iters)
    assert out["windows_stage1_time_limit"] == 0
    assert out["windows_earliness_time_limit"] == 0


def test_moves_and_continuity_counts_moves_and_kept_machines() -> None:
    records = [
        _rec("m1", "B1", 1, "S1", 10.0),
        _rec("m1", "B2", 2, "S1", 10.0),  # m1 moves B1 -> B2
        _rec("m2", "B1", 1, "S1", 10.0),
        _rec("m2", "B1", 2, "S1", 10.0),  # m2 stays on B1
        _rec("m1", "B2", 3, "S1", 0.0),  # idle: production below WORK_EPS, excluded
    ]
    moves, continuity = _moves_and_continuity(records, {"S1": 0})
    assert moves == 1
    # B1 day1 machines {m1, m2}, day2 {m2}: kept 1 of 2
    assert continuity == pytest.approx(0.5)


def test_moves_and_continuity_empty_records() -> None:
    moves, continuity = _moves_and_continuity([], {})
    assert moves == 0
    assert math.isnan(continuity)


def test_add_relatives_computes_best_and_baseline() -> None:
    df = _frame().drop(columns=["rel_best", "rel_baseline", "share_of_volume"])
    out = add_relatives(df)
    # best known per (context, size) is 100.0 (the mip baseline)
    assert out.loc[out.method == "sa", "rel_best"].round(3).tolist() == [0.95, 0.88]
    # baseline per method: mip 100, sa 95
    assert out.loc[(out.method == "mip") & out.baseline, "rel_baseline"].iloc[0] == 1.0
    assert out.loc[(out.method == "sa") & ~out.baseline, "rel_baseline"].round(3).iloc[
        0
    ] == pytest.approx(round(88 / 95, 3))
    assert out.loc[out.method == "mip", "share_of_volume"].round(2).tolist() == [1.0, 0.9]


def test_fmt_formats_none_nan_and_values() -> None:
    assert _fmt(None) == "--"
    assert _fmt(float("nan")) == "--"
    assert _fmt(1234.5, 1) == "1,234.5"
    assert _fmt(0.5, 2) == "0.50"


def test_gurobi_work_rates_parses_logs(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    runs.mkdir()
    (runs / "a_mip.gurobi.log").write_text(
        "Explored 100 nodes in 200.0 seconds (150.0 work units)\n"
        "Explored 10 nodes in 5.0 seconds (4.0 work units)\n",  # below min_seconds
        encoding="utf-8",
    )
    df = gurobi_work_rates(tmp_path, min_seconds=100.0)
    assert len(df) == 1
    assert df.iloc[0]["run_id"] == "a_mip"
    assert df.iloc[0]["work_per_s"] == pytest.approx(0.75)


def test_table_baselines_writes_rows(tmp_path: Path) -> None:
    out = tmp_path / "baselines.tex"
    table_baselines(_frame(), out)
    text = out.read_text(encoding="utf-8")
    assert "Kamloops & 6" in text
    assert "100.0" in text  # mip share of volume
    assert "\\bottomrule" in text


def test_table_window_outcomes_writes_rows(tmp_path: Path) -> None:
    out = tmp_path / "window_outcomes.tex"
    table_window_outcomes(_frame(), out)
    text = out.read_text(encoding="utf-8")
    assert "MIP & 6" in text
    assert "SA & 6" in text
    assert "\\bottomrule" in text


def test_numbers_writes_macros(tmp_path: Path) -> None:
    out = tmp_path / "numbers.tex"
    rates = pd.DataFrame({"work_per_s": [0.5, 0.6, 0.7, 0.8]})
    numbers(_frame(), out, rates)
    text = out.read_text(encoding="utf-8")
    assert "\\newcommand{\\NRuns}{4}" in text
    assert "\\newcommand{\\NRollingRuns}{2}" in text
    assert "\\newcommand{\\GurobiWorkRateMedian}{0.65}" in text
    assert "\\newcommand{\\TinyThreshold}{0.001}" in text


def test_spec_reads_the_spec_block(tmp_path: Path) -> None:
    jp = tmp_path / "r.json"
    jp.write_text(json.dumps({"spec": {"baseline": True, "solver": "mip"}}), encoding="utf-8")
    spec = _spec(jp)
    assert spec["baseline"] is True
    assert spec["solver"] == "mip"


def test_material_violations_restores_tolerance() -> None:
    import fhops.evaluation.sequencing as seq
    from fhops.evaluation.metrics.kpis import compute_kpis
    from fhops.scenario.contract import Problem
    from fhops.scenario.io import load_scenario

    scenario = load_scenario(str(SCENARIO))
    problem = Problem.from_scenario(scenario)
    assignments = pd.DataFrame(columns=["machine_id", "block_id", "day", "shift_id", "assigned"])
    saved = seq.SEQUENCING_TOLERANCE
    count = material_violations(problem, assignments)
    assert isinstance(count, int)
    assert saved == seq.SEQUENCING_TOLERANCE
    # an empty plan has no violations, and the tolerance is TINY_M3 during the call
    assert count == int(compute_kpis(problem, assignments)["sequencing_violation_count"])


def test_tiny_m3_is_one_thousandth() -> None:
    assert TINY_M3 == 1e-3


def _full_frame() -> pd.DataFrame:
    """A frame with every column the figure functions read, across both methods and sizes."""
    rows = []
    for method in ["sa", "mip"]:
        for size in [6, 18, 40]:
            for ctx in ["ka", "ni", "pg"]:
                for lock in [1, 7, 14]:
                    for theta in [2, 4, 8, 16]:
                        rows.append(
                            {
                                "context": ctx,
                                "size": size,
                                "method": method,
                                "baseline": False,
                                "lock_days": lock,
                                "theta_weeks": theta,
                                "rel_best": 0.9 + 0.01 * (lock % 3),
                                "wall_time_s": 1000.0 + size * 10,
                                "continuity": 0.5,
                            }
                        )
                rows.append(
                    {
                        "context": ctx,
                        "size": size,
                        "method": method,
                        "baseline": True,
                        "lock_days": 112,
                        "theta_weeks": None,
                        "rel_best": 1.0,
                        "wall_time_s": 2000.0,
                        "continuity": 0.4,
                    }
                )
    return pd.DataFrame(rows)


def test_fig_delivered_writes_a_pdf(tmp_path: Path) -> None:
    out = tmp_path / "fig_delivered.pdf"
    fig_delivered(_full_frame(), out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_fig_effort_writes_a_pdf(tmp_path: Path) -> None:
    out = tmp_path / "fig_effort.pdf"
    fig_effort(_full_frame(), out)
    assert out.exists()
    assert out.stat().st_size > 0


def _minimal_run_json(run_id: str, baseline: bool, delivered: float) -> dict[str, object]:
    return {
        "run_id": run_id,
        "spec": {
            "baseline": baseline,
            "solver": "mip",
            "context": "ka",
            "size": "6",
            "sub_days": 112 if baseline else 14,
            "lock_days": 112 if baseline else 7,
            "master_days": 112,
            "theta_weeks": None if baseline else 2,
            "mip_time_limit": 30,
            "mip_earliness_time_limit": 30,
            "mip_solver": "gurobi",
        },
        "plan_summary": {
            "iterations": [
                {
                    "start_day": 1,
                    "status": "solved",
                    "empty": False,
                    "runtime_s": 1.0,
                    "warnings": [],
                }
            ]
        },
        "n_locked_assignments": 0,
        "wall_time_s": 10.0,
        "kpis": {
            "total_production": delivered,
            "remaining_work_total": 0.0,
            "sequencing_violation_count": 0,
        },
    }


def test_collect_builds_the_paper_set(tmp_path: Path) -> None:
    grid = tmp_path / "grid" / "runs"
    grid.mkdir(parents=True)
    (grid / "ka_6_baseline_mip.json").write_text(
        json.dumps(_minimal_run_json("ka_6_baseline_mip", True, 100.0)), encoding="utf-8"
    )
    (grid / "ka_6_sub14_lock7_mip.json").write_text(
        json.dumps(_minimal_run_json("ka_6_sub14_lock7_mip", False, 90.0)), encoding="utf-8"
    )
    for name in ["ka_6_baseline_mip", "ka_6_sub14_lock7_mip"]:
        (grid / f"{name}_assignments.csv").write_text(
            "machine_id,block_id,day,shift_id,assigned,production\n", encoding="utf-8"
        )
    paper, superseded = collect(tmp_path / "grid", [], MODEL_REPO, 1, "mip")
    assert len(paper) == 2
    assert superseded.empty
    assert set(paper.run_id) == {"ka_6_baseline_mip", "ka_6_sub14_lock7_mip"}
    assert paper.loc[paper.run_id == "ka_6_sub14_lock7_mip", "rel_best"].iloc[0] == pytest.approx(
        0.9
    )


def test_run_metrics_replays_a_run(tmp_path: Path) -> None:
    jp = tmp_path / "runs" / "ka_6_sub14_lock7_mip.json"
    jp.parent.mkdir()
    jp.write_text(
        json.dumps(_minimal_run_json("ka_6_sub14_lock7_mip", False, 0.0)), encoding="utf-8"
    )
    ap = jp.with_name("ka_6_sub14_lock7_mip_assignments.csv")
    ap.write_text("machine_id,block_id,day,shift_id,assigned,production\n", encoding="utf-8")
    row = run_metrics((str(jp), str(ap), str(SCENARIO)))
    assert row["run_id"] == "ka_6_sub14_lock7_mip"
    assert row["delivered_m3"] == 0.0
    assert row["windows"] == 1
    assert row["moves"] == 0


def test_main_runs_end_to_end(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    grid = tmp_path / "grid" / "runs"
    grid.mkdir(parents=True)
    (grid / "ka_6_baseline_mip.json").write_text(
        json.dumps(_minimal_run_json("ka_6_baseline_mip", True, 100.0)), encoding="utf-8"
    )
    (grid / "ka_6_sub14_lock7_mip.json").write_text(
        json.dumps(_minimal_run_json("ka_6_sub14_lock7_mip", False, 90.0)), encoding="utf-8"
    )
    for name in ["ka_6_baseline_mip", "ka_6_sub14_lock7_mip"]:
        (grid / f"{name}_assignments.csv").write_text(
            "machine_id,block_id,day,shift_id,assigned,production\n", encoding="utf-8"
        )
    import analyze_rerun as ar

    monkeypatch.setattr(ar, "ROOT", tmp_path)
    monkeypatch.setattr(
        "sys.argv",
        [
            "analyze_rerun.py",
            "--rerun-dir",
            str(tmp_path / "grid"),
            "--out-tag",
            "test",
            "--methods",
            "mip",
            "--workers",
            "1",
            "--model-repo",
            str(MODEL_REPO),
        ],
    )
    assert main() == 0
    assert (tmp_path / "results" / "test" / "runs_metrics.csv").exists()
    assert (tmp_path / "manuscript" / "tables" / "baselines_test.tex").exists()
    assert (tmp_path / "manuscript" / "figures" / "fig_delivered_test.pdf").exists()
    assert (tmp_path / "manuscript" / "generated" / "numbers_test.tex").exists()
