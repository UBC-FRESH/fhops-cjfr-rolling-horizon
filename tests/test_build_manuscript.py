"""Unit tests for ``scripts.build_manuscript``.

The build runs an external binary, so the tests patch the subprocess call and check the log
inspection and the overall status.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

import build_manuscript as bm


def test_build_document_reports_ok(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def fake_run(*args: object, **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(returncode=0, stdout="Output written", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = bm.build_document("tectonic", "main.tex", tmp_path, "build")
    assert result.ok
    assert result.returncode == 0
    assert result.undefined == ()


def test_build_document_reports_undefined(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def fake_run(*args: object, **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(
            returncode=0, stdout="LaTeX Warning: There were undefined references.", stderr=""
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = bm.build_document("tectonic", "main.tex", tmp_path, "build")
    assert not result.ok
    assert result.undefined


def test_build_document_reports_a_nonzero_exit(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def fake_run(*args: object, **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(returncode=1, stdout="", stderr="error: halted")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = bm.build_document("tectonic", "main.tex", tmp_path, "build")
    assert not result.ok
    assert result.returncode == 1


def test_main_reports_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_build(*args: object, **kwargs: object) -> bm.BuildResult:
        return bm.BuildResult("main.tex", 1, ())

    monkeypatch.setattr(bm, "build_document", fake_build)
    assert bm.main() == 1


def test_main_reports_success(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_build(*args: object, **kwargs: object) -> bm.BuildResult:
        return bm.BuildResult("main.tex", 0, ())

    monkeypatch.setattr(bm, "build_document", fake_build)
    assert bm.main() == 0
