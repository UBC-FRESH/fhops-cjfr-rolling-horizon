"""Unit tests for ``scripts.package_submission``.

The flattening and the package build are tested on a small temporary manuscript tree.
"""

from __future__ import annotations

from pathlib import Path

import package_submission as ps


def _mini_manuscript(root: Path) -> None:
    (root / "sections").mkdir(parents=True)
    (root / "tables").mkdir()
    (root / "figures").mkdir()
    (root / "generated").mkdir()
    (root / "build").mkdir()
    (root / "main.tex").write_text(
        "\\documentclass{article}\n\\input{metadata}\n\\input{sections/body}\n"
        "\\IfFileExists{generated/numbers.tex}{\\input{generated/numbers}}{}\n"
        "\\includegraphics{figures/fig.pdf}\n"
        "\\bibliographystyle{cjfr-apalike-doi}\n\\bibliography{references}\n",
        encoding="utf-8",
    )
    (root / "metadata.tex").write_text("% metadata\n", encoding="utf-8")
    (root / "sections" / "body.tex").write_text("Body. \\input{tables/inline}\n", encoding="utf-8")
    (root / "tables" / "inline.tex").write_text(
        "\\begin{tabular}{l}a\\end{tabular}\n", encoding="utf-8"
    )
    (root / "generated" / "numbers.tex").write_text("\\newcommand{\\X}{1}\n", encoding="utf-8")
    (root / "references.bib").write_text("@article{k, title={T}}\n", encoding="utf-8")
    (root / "figures" / "fig.pdf").write_bytes(b"%PDF-1.4 fake")
    (root / "figures" / "fig_smoke.pdf").write_bytes(b"%PDF-1.4 fake")
    (root / "build" / "main.bbl").write_text(
        "\\begin{thebibliography}{1}\\end{thebibliography}\n", encoding="utf-8"
    )


def test_inline_replaces_nested_inputs(tmp_path: Path, monkeypatch: object) -> None:
    monkeypatch.setattr(ps, "MANUSCRIPT", tmp_path)  # type: ignore[attr-defined]
    _mini_manuscript(tmp_path)
    text = ps.inline((tmp_path / "main.tex").read_text(encoding="utf-8"))
    assert "\\input{" not in text
    assert "Body." in text
    assert "begin{tabular}" in text


def test_main_writes_a_flat_package(tmp_path: Path, monkeypatch: object) -> None:
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir()
    _mini_manuscript(manuscript)
    package = tmp_path / "package"
    monkeypatch.setattr(ps, "MANUSCRIPT", manuscript)  # type: ignore[attr-defined]
    monkeypatch.setattr(ps, "PACKAGE", package)  # type: ignore[attr-defined]
    monkeypatch.setattr(ps, "ROOT", tmp_path)  # type: ignore[attr-defined]
    assert ps.main() == 0
    flat = (package / "manuscript.tex").read_text(encoding="utf-8")
    assert "\\input{" not in flat
    assert "thebibliography" in flat  # the bbl was inlined
    assert "\\includegraphics{fig.pdf}" in flat  # the path was flattened
    assert (package / "fig.pdf").exists()
    assert not (package / "fig_smoke.pdf").exists()  # interim and smoke figures are skipped
    assert (package / "references.bib").exists()
    assert (package / "numbers.tex").exists()
    assert not (package / "generated").exists()  # no nested directories
    assert "generated/numbers.tex" not in flat
    assert "\\IfFileExists{numbers.tex}" in flat  # guard rewritten to the flat path


def test_main_fails_without_main_tex(tmp_path: Path, monkeypatch: object) -> None:
    monkeypatch.setattr(ps, "MANUSCRIPT", tmp_path)  # type: ignore[attr-defined]
    assert ps.main() == 1
