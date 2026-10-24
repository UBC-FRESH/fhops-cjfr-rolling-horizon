#!/usr/bin/env python3
r"""Flatten the manuscript source into one folder for ScholarOne.

ScholarOne prefers the LaTeX sources in a single folder, with the bibliography inlined and the
figures referenced without directory prefixes. This script writes ``submission/package/``:

- ``manuscript.tex``: ``manuscript/main.tex`` with every ``\input`` inlined (sections, tables,
  metadata, generated numbers) and every ``\includegraphics{figures/...}`` rewritten to the file
  name, followed by the bibliography environment from the built ``.bbl``.
- the figure PDFs, and ``references.bib``.

It also copies the built PDFs (the paper, the supplement and the cover letter) into the folder.

Usage
-----
    python scripts/package_submission.py
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript"
PACKAGE = ROOT / "submission" / "package"
INPUT = re.compile(r"\\input\{([^}]+)\}")
INCLUDE = re.compile(r"\\includegraphics(\[[^\]]*\])?\{([^}]+)\}")


def inline(tex: str) -> str:
    r"""Replace every ``\input{...}`` with the target file's content, recursively.

    Every path is relative to ``manuscript/``, as LaTeX resolves them from the main file.

    Parameters
    ----------
    tex : str
        The LaTeX source.

    Returns
    -------
    str
        The source with the includes inlined.
    """

    def repl(match: re.Match[str]) -> str:
        target = MANUSCRIPT / f"{match.group(1)}.tex"
        return inline(target.read_text(encoding="utf-8"))

    return INPUT.sub(repl, tex)


def main() -> int:
    """Write the flattened package.

    Returns
    -------
    int
        0 on success, 1 when a needed file is missing.
    """
    bbl = MANUSCRIPT / "build" / "main.bbl"
    main_tex = MANUSCRIPT / "main.tex"
    if not main_tex.exists():
        print("manuscript/main.tex is missing; build the paper first", file=sys.stderr)
        return 1
    # A missing or stale .bbl would silently ship a bibliography that does not match the cited keys,
    # so refuse to package. tectonic only emits the .bbl with --keep-intermediates.
    if not bbl.exists() or bbl.stat().st_mtime < max(
        (MANUSCRIPT / "references.bib").stat().st_mtime, main_tex.stat().st_mtime
    ):
        print(
            "manuscript/build/main.bbl is missing or older than the sources; rebuild with "
            "`tectonic --keep-intermediates -o build main.tex` before packaging",
            file=sys.stderr,
        )
        return 1
    PACKAGE.mkdir(parents=True, exist_ok=True)
    tex = inline(main_tex.read_text(encoding="utf-8"))

    def include_repl(m: re.Match[str]) -> str:
        return "\\includegraphics" + (m.group(1) or "") + "{" + Path(m.group(2)).name + "}"

    tex = INCLUDE.sub(include_repl, tex)
    if bbl.exists():
        bbl_text = bbl.read_text(encoding="utf-8")
        bib = re.compile(r"\\bibliographystyle\{[^}]+\}\s*\\bibliography\{[^}]+\}")
        tex = bib.sub(lambda m: bbl_text, tex)
    (PACKAGE / "manuscript.tex").write_text(tex, encoding="utf-8")
    for pattern in ["figures/*.pdf", "figures/*.png"]:
        for fig in MANUSCRIPT.glob(pattern):
            if "_interim" in fig.stem or "_smoke" in fig.stem:
                continue
            shutil.copy2(fig, PACKAGE / fig.name)
    shutil.copy2(MANUSCRIPT / "references.bib", PACKAGE / "references.bib")
    # the paper guards the generated macros with \IfFileExists, so the file must exist at this path
    generated = PACKAGE / "generated"
    generated.mkdir(exist_ok=True)
    shutil.copy2(MANUSCRIPT / "generated" / "numbers.tex", generated / "numbers.tex")
    for name, target in [
        ("main.pdf", "fhops-cjfr-main.pdf"),
        ("supplement.pdf", "fhops-cjfr-supplement.pdf"),
        ("cover-letter.pdf", "fhops-cjfr-cover-letter.pdf"),
    ]:
        if (MANUSCRIPT / "build" / name).exists():
            shutil.copy2(MANUSCRIPT / "build" / name, PACKAGE / target)
    cover = ROOT / "submission" / "cover-letter.tex"
    if cover.exists():
        shutil.copy2(cover, PACKAGE / "cover-letter.tex")
    print(f"wrote {PACKAGE} ({len(list(PACKAGE.iterdir()))} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
