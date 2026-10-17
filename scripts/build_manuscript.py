#!/usr/bin/env python3
r"""Build the manuscript, the supplement, and the cover letter, and fail on errors.

The paper's numbers are generated, so a green dashboard must also mean that the paper builds. This
script runs tectonic on the three documents and inspects each log for errors and for undefined
references or citations. It is the command behind the ``manuscript`` gate in
``scripts/dashboard.py`` (ADR 0001).

The tectonic binary is taken from the ``TECTONIC`` environment variable, or from ``PATH``.

Usage
-----
    python scripts/build_manuscript.py
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# (document, working directory, output directory) for each document to build.
DOCUMENTS: tuple[tuple[str, Path, str], ...] = (
    ("main.tex", ROOT / "manuscript", "build"),
    ("supplement.tex", ROOT / "manuscript", "build"),
    ("cover-letter.tex", ROOT / "submission", str(ROOT / "manuscript" / "build")),
)
UNDEFINED = re.compile(
    r"undefined (reference|citation|control sequence)|Undefined control sequence"
)


@dataclass(frozen=True)
class BuildResult:
    """The outcome of one document build.

    Attributes
    ----------
    name : str
        The document file name.
    returncode : int
        The tectonic exit status.
    undefined : tuple[str, ...]
        Lines in the log that report an undefined reference or citation.
    """

    name: str
    returncode: int
    undefined: tuple[str, ...]

    @property
    def ok(self) -> bool:
        """Whether the build succeeded and the log has no undefined references."""
        return self.returncode == 0 and not self.undefined


def build_document(tectonic: str, document: str, workdir: Path, out: str) -> BuildResult:
    """Build one document with tectonic and inspect its log.

    Parameters
    ----------
    tectonic : str
        The tectonic executable.
    document : str
        The document file name, relative to ``workdir``.
    workdir : pathlib.Path
        The directory that holds the document.
    out : str
        The output directory, relative to ``workdir`` or absolute.

    Returns
    -------
    BuildResult
        The exit status and any undefined-reference lines.
    """
    completed = subprocess.run(
        [tectonic, "-o", out, document],
        cwd=workdir,
        capture_output=True,
        text=True,
        check=False,
    )
    output = completed.stdout + completed.stderr
    undefined = tuple(line.strip() for line in output.splitlines() if UNDEFINED.search(line))
    return BuildResult(document, completed.returncode, undefined)


def main() -> int:
    """Build every document and report.

    Returns
    -------
    int
        0 when every document builds with no undefined references, 1 otherwise.
    """
    tectonic = os.environ.get("TECTONIC", "tectonic")
    results = [build_document(tectonic, doc, workdir, out) for doc, workdir, out in DOCUMENTS]
    for result in results:
        status = "ok" if result.ok else "FAILED"
        print(f"{result.name}: {status} (exit {result.returncode})")
        for line in result.undefined:
            print(f"  {line}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
