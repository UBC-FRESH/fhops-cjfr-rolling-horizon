"""Unit tests for the table and word-count scripts.

Each generator is tested on a small fixture, and the word counter on LaTeX fragments. The table
generators read from ``ROOT``, which is monkeypatched to a temporary directory.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

import make_supplement_tables as mst
import make_table_scenarios as mts
import wordcount as wc


def test_wordcount_main(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        wc, "SECTIONS", Path(__file__).resolve().parents[1] / "manuscript" / "sections"
    )
    assert wc.main() == 0
    out = capsys.readouterr().out
    assert "BODY" in out
    assert "ABSTRACT" in out


def test_make_table_scenarios_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    base = tmp_path / "data" / "input" / "scenarios" / "ka_6"
    _write_scenario_bundle(base)
    monkeypatch.setattr(mts, "ROOT", tmp_path)
    monkeypatch.setattr(mts, "AREAS", {"ka": "Kamloops"})
    monkeypatch.setattr(mts, "SIZES", ["6"])
    monkeypatch.setattr("sys.argv", ["make_table_scenarios.py", "--model-repo", str(tmp_path)])
    assert mts.main() == 0
    assert (tmp_path / "results" / "scenarios.csv").exists()
    assert (tmp_path / "manuscript" / "tables" / "scenarios.tex").exists()


def test_make_supplement_tables_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cal = tmp_path / "results" / "calibration"
    cal.mkdir(parents=True)
    pd.DataFrame(
        {
            "window": ["ka_6_sub112_lock7"],
            "stage": [1],
            "checkpoint_s": [1800],
            "shortfall_vs_final_pct": [0.5],
            "gap_pct": [0.4],
        }
    ).to_csv(cal / "trajectory_checkpoints.csv", index=False)
    pd.DataFrame(
        {"window": ["ka_6_sub112_lock7"], "stage": [1], "seconds": [2.8], "work_units": [2.0]}
    ).to_csv(cal / "stage_totals.csv", index=False)
    pd.DataFrame({"window": ["ka_6_sub112_lock7"], "binaries": [16079]}).to_csv(
        cal / "model_sizes.csv", index=False
    )
    probe = tmp_path / "results" / "solver_probe"
    (probe / "gurobi").mkdir(parents=True)
    doc = {"summary": {"iterations": [{"planned_delivered": 100.0, "locked_delivered": 50.0}]}}
    (probe / "ka_40_sub14_lock7.json").write_text(json.dumps(doc), encoding="utf-8")
    (probe / "gurobi" / "ka_40_sub14_lock7.json").write_text(json.dumps(doc), encoding="utf-8")
    monkeypatch.setattr(mst, "ROOT", tmp_path)
    assert mst.main() == 0
    assert (tmp_path / "manuscript" / "tables" / "calibration.tex").exists()
    assert (tmp_path / "manuscript" / "tables" / "solver_probe.tex").exists()


def _write_scenario_bundle(base: Path) -> None:
    (base / "data").mkdir(parents=True)
    pd.DataFrame(
        {
            "id": ["B1", "B2"],
            "landing_id": ["L1", "L2"],
            "work_required": [100.0, 200.0],
            "ground_slope_percent": [10.0, 20.0],
            "avg_stem_size_m3": [0.5, 0.7],
        }
    ).to_csv(base / "data" / "blocks.csv", index=False)
    pd.DataFrame({"id": ["m1", "m2"], "role": ["feller_buncher", "loader"]}).to_csv(
        base / "data" / "machines.csv", index=False
    )
    pd.DataFrame({"id": ["L1", "L2"], "daily_capacity": [2, 2]}).to_csv(
        base / "data" / "landings.csv", index=False
    )
    (base / "scenario.yaml").write_text("num_days: 112\n", encoding="utf-8")


def test_scenario_row_reads_a_bundle(tmp_path: Path) -> None:
    base = tmp_path / "ka_6"
    _write_scenario_bundle(base)
    row = mts.scenario_row(base, "ka", "Kamloops", "6")
    assert row["scenario"] == "ka_6"
    assert row["area"] == "Kamloops"
    assert row["blocks"] == 2
    assert row["machines"] == 2
    assert row["machines_per_role"] == "1/0/0/1"
    assert row["landings"] == 2
    assert row["landing_daily_capacity"] == 2
    assert row["num_days"] == 112
    assert row["total_volume_m3"] == pytest.approx(300.0)
    assert row["mean_block_volume_m3"] == pytest.approx(150.0)
    assert row["mean_slope_pct"] == pytest.approx(15.0)
    assert row["mean_stem_size_m3"] == pytest.approx(0.6)


def test_wordcount_strips_commands_and_floats() -> None:
    tex = (
        "\\section{Intro}\n"
        "This is a sentence with \\cite{key2020} and $x + y$ math.\n"
        "\\begin{table} a table \\end{table}\n"
        "% a comment\n"
        "\\pending{to be replaced}\n"
    )
    body, pending = wc.words(tex)
    assert body == 8  # "This is a sentence with and math."
    assert pending == 3  # "to be replaced"


def test_wordcount_strip_braced_balanced() -> None:
    text = "a \\cmd{one {two} three} b"
    rest, removed = wc._strip_braced(text, "cmd")
    assert rest == "a  b"
    assert removed == "one {two} three"


def test_wordcount_counts_only_alphanumeric() -> None:
    body, _ = wc.words("one two 3 four -- five")
    assert body == 5


def test_calibration_table_writes_rows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cal = tmp_path / "results" / "calibration"
    cal.mkdir(parents=True)
    pd.DataFrame(
        {
            "window": ["ka_6_sub112_lock7", "ka_6_sub112_lock7"],
            "stage": [1, 2],
            "checkpoint_s": [1800, 300],
            "shortfall_vs_final_pct": [0.5, 1.5],
            "gap_pct": [0.4, 0.0],
        }
    ).to_csv(cal / "trajectory_checkpoints.csv", index=False)
    pd.DataFrame(
        {"window": ["ka_6_sub112_lock7"], "stage": [1], "seconds": [2.8], "work_units": [2.0]}
    ).to_csv(cal / "stage_totals.csv", index=False)
    pd.DataFrame({"window": ["ka_6_sub112_lock7"], "binaries": [16079]}).to_csv(
        cal / "model_sizes.csv", index=False
    )
    monkeypatch.setattr(mst, "ROOT", tmp_path)
    out = tmp_path / "calibration.tex"
    mst.calibration_table(out)
    text = out.read_text(encoding="utf-8")
    assert "Kamloops & 6 & 112" in text
    assert "16,079" in text
    assert "optimal (2.8 s)" in text
    assert "\\bottomrule" in text


def test_probe_table_writes_rows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    probe = tmp_path / "results" / "solver_probe"
    (probe / "gurobi").mkdir(parents=True)
    doc = {"summary": {"iterations": [{"planned_delivered": 100.0, "locked_delivered": 50.0}]}}
    (probe / "ka_40_sub14_lock7.json").write_text(json.dumps(doc), encoding="utf-8")
    (probe / "gurobi" / "ka_40_sub14_lock7.json").write_text(json.dumps(doc), encoding="utf-8")
    monkeypatch.setattr(mst, "ROOT", tmp_path)
    out = tmp_path / "solver_probe.tex"
    mst.probe_table(out)
    text = out.read_text(encoding="utf-8")
    assert "Kamloops & 40 & 14" in text
    assert "100" in text
    assert "50" in text
    assert "\\bottomrule" in text
