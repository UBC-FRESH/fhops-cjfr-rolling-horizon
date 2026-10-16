"""Unit tests for ``scripts.audit_rerun_inputs``.

The audit must be able to fail. Each negative control breaks one field of a valid run and asserts
that the audit reports exactly that failure, while the unmodified run passes.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from audit_rerun_inputs import (
    REPLAY_TOLERANCE,
    RunSpec,
    audit_one,
    expected_windows,
    main,
    paper_set,
)

MODEL_REPO = Path(__file__).resolve().parents[1].parent / "jaffray-masc-fhops-model"
SCENARIO = MODEL_REPO / "data" / "input" / "scenarios" / "ka_6" / "scenario.yaml"

pytestmark = pytest.mark.skipif(not SCENARIO.exists(), reason="model repo not present")


def _spec(**overrides: object) -> RunSpec:
    spec: RunSpec = {
        "baseline": False,
        "master_days": 28,
        "lock_days": 7,
        "solver": "mip",
        "context": "ka",
        "size": "6",
        "sub_days": 14,
        "mip_time_limit": 30,
    }
    spec.update(overrides)  # type: ignore[typeddict-item]
    return spec


def _iterations(lock: int, master: int) -> list[dict[str, int]]:
    return [{"start_day": 1 + i * lock} for i in range((master + lock - 1) // lock)]


def _run_doc(
    spec: RunSpec, iterations: list[dict[str, int]], delivered: float, rows: int
) -> dict[str, object]:
    return {
        "run_id": "ka_6_sub14_lock7_mip",
        "spec": dict(spec),
        "plan_summary": {"iterations": iterations},
        "n_locked_assignments": rows,
        "kpis": {"total_production": delivered},
    }


def _write(tmp_path: Path, doc: dict[str, object], assignments: str) -> tuple[str, str]:
    runs = tmp_path / "runs"
    runs.mkdir(exist_ok=True)
    jp = runs / "ka_6_sub14_lock7_mip.json"
    jp.write_text(json.dumps(doc), encoding="utf-8")
    ap = runs / "ka_6_sub14_lock7_mip_assignments.csv"
    ap.write_text(assignments, encoding="utf-8")
    return str(jp), str(ap)


def _assignments(rows: int) -> str:
    header = "machine_id,block_id,day,shift_id,assigned,production\n"
    body = "".join(f"fb_01,B74735,{d},S1,1,100.0\n" for d in range(1, rows + 1))
    return header + body


def test_expected_windows_rolling() -> None:
    assert expected_windows(_spec(master_days=112, lock_days=1)) == 112
    assert expected_windows(_spec(master_days=112, lock_days=7)) == 16
    assert expected_windows(_spec(master_days=112, lock_days=14)) == 8
    assert expected_windows(_spec(master_days=28, lock_days=7)) == 4


def test_expected_windows_baseline() -> None:
    assert expected_windows(_spec(baseline=True, master_days=112, lock_days=112)) == 1


def test_audit_passes_a_valid_run(tmp_path: Path) -> None:
    spec = _spec()
    iters = _iterations(spec["lock_days"], spec["master_days"])
    doc = _run_doc(spec, iters, delivered=0.0, rows=0)
    jp, ap = _write(tmp_path, doc, _assignments(0))
    row = audit_one((jp, ap, str(SCENARIO)))
    assert row["passed"] is True, row["failures"]


def test_audit_flags_a_dropped_window(tmp_path: Path) -> None:
    spec = _spec()
    iters = _iterations(spec["lock_days"], spec["master_days"])[:-1]
    doc = _run_doc(spec, iters, delivered=0.0, rows=0)
    jp, ap = _write(tmp_path, doc, _assignments(0))
    row = audit_one((jp, ap, str(SCENARIO)))
    assert row["passed"] is False
    assert "windows 3 != 4" in row["failures"]


def test_audit_flags_a_wrong_row_count(tmp_path: Path) -> None:
    spec = _spec()
    iters = _iterations(spec["lock_days"], spec["master_days"])
    doc = _run_doc(spec, iters, delivered=0.0, rows=5)
    jp, ap = _write(tmp_path, doc, _assignments(4))
    row = audit_one((jp, ap, str(SCENARIO)))
    assert row["passed"] is False
    assert "n_locked_assignments 5 != CSV rows 4" in row["failures"]


def test_audit_flags_a_wrong_delivered_volume(tmp_path: Path) -> None:
    spec = _spec()
    iters = _iterations(spec["lock_days"], spec["master_days"])
    doc = _run_doc(spec, iters, delivered=1.0, rows=0)
    jp, ap = _write(tmp_path, doc, _assignments(0))
    row = audit_one((jp, ap, str(SCENARIO)))
    assert row["passed"] is False
    assert "replayed delivered" in row["failures"]


def test_audit_flags_an_error_key(tmp_path: Path) -> None:
    spec = _spec()
    iters = _iterations(spec["lock_days"], spec["master_days"])
    doc = _run_doc(spec, iters, delivered=0.0, rows=0)
    doc["error"] = "boom"
    jp, ap = _write(tmp_path, doc, _assignments(0))
    row = audit_one((jp, ap, str(SCENARIO)))
    assert row["passed"] is False
    assert "run carries an error: boom" in row["failures"]


def test_audit_flags_wrong_start_days(tmp_path: Path) -> None:
    spec = _spec()
    iters = [{"start_day": 1}, {"start_day": 9}, {"start_day": 15}, {"start_day": 22}]
    doc = _run_doc(spec, iters, delivered=0.0, rows=0)
    jp, ap = _write(tmp_path, doc, _assignments(0))
    row = audit_one((jp, ap, str(SCENARIO)))
    assert row["passed"] is False
    assert "window start days do not advance by the lock span" in row["failures"]


def test_paper_set_replaces_superseded_baselines(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    grid = tmp_path / "grid" / "runs"
    grid.mkdir(parents=True)
    (grid / "ka_40_baseline_mip.json").write_text(
        json.dumps({"spec": {"baseline": True, "solver": "mip"}}), encoding="utf-8"
    )
    (grid / "ka_6_sub14_lock7_mip.json").write_text(
        json.dumps({"spec": {"baseline": False, "solver": "mip"}}), encoding="utf-8"
    )
    override = tmp_path / "override" / "runs"
    override.mkdir(parents=True)
    (override / "ka_40_baseline_mip.json").write_text(
        json.dumps({"spec": {"baseline": True, "solver": "mip"}}), encoding="utf-8"
    )
    monkeypatch.setattr("audit_rerun_inputs.GRID", tmp_path / "grid")
    monkeypatch.setattr("audit_rerun_inputs.BASELINE_DIRS", [tmp_path / "override"])
    paths = paper_set()
    names = [p.name for p in paths]
    assert "ka_6_sub14_lock7_mip.json" in names
    assert names.count("ka_40_baseline_mip.json") == 1
    kept = [p for p in paths if p.name == "ka_40_baseline_mip.json"]
    assert kept[0].parent.parent.name == "override"


def test_replay_tolerance_is_relative() -> None:
    assert REPLAY_TOLERANCE == 1e-6
    assert abs(100.0 - 100.0000001) <= REPLAY_TOLERANCE * max(1.0, abs(100.0))


def test_main_writes_the_audit_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import audit_rerun_inputs as ari

    grid = tmp_path / "grid" / "runs"
    grid.mkdir(parents=True)
    spec = _spec()
    iters = _iterations(spec["lock_days"], spec["master_days"])
    doc = _run_doc(spec, iters, delivered=0.0, rows=0)
    (grid / "ka_6_sub14_lock7_mip.json").write_text(json.dumps(doc), encoding="utf-8")
    (grid / "ka_6_sub14_lock7_mip_assignments.csv").write_text(_assignments(0), encoding="utf-8")
    monkeypatch.setattr(ari, "GRID", tmp_path / "grid")
    monkeypatch.setattr(ari, "BASELINE_DIRS", [])
    monkeypatch.setattr(ari, "ROOT", tmp_path)
    monkeypatch.setattr(
        "sys.argv",
        ["audit_rerun_inputs.py", "--workers", "1", "--model-repo", str(MODEL_REPO)],
    )
    assert main() == 0
    assert (tmp_path / "results" / "audit" / "runs_audit.csv").exists()
