#!/usr/bin/env python3
"""Approximate CJFR word counts: abstract (limit 200) and Introduction-to-Discussion (limit 6000).

The body count covers ``sections/introduction``, ``methods``, ``results`` and ``discussion``
(including Conclusions, which sits in the discussion file) and excludes figure/table environments,
captions, comments and citations. Text inside ``\\pending{}`` is reported separately because it
will be replaced. The numbers are approximations of a word-processor count.

Usage
-----
    python scripts/wordcount.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ROOT / "manuscript" / "sections"


def _strip_braced(text: str, command: str) -> tuple[str, str]:
    """Remove ``\\command{...}`` (balanced braces); return (remaining text, removed contents)."""
    out, removed, i = [], [], 0
    token = "\\" + command + "{"
    while True:
        j = text.find(token, i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j])
        k, depth = j + len(token), 1
        while k < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[k], 0)
            k += 1
        removed.append(text[j + len(token) : k - 1])
        i = k
    return "".join(out), " ".join(removed)


def words(tex: str) -> tuple[int, int]:
    tex = re.sub(r"(?<!\\)%.*", "", tex)
    tex = re.sub(r"\\begin\{(figure|table)\}.*?\\end\{\1\}", " ", tex, flags=re.S)
    tex, pending = _strip_braced(tex, "pending")
    tex = re.sub(r"\\cite[pt]?\*?(\[[^\]]*\])*\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\(ref|label|eqref)\{[^}]*\}", " ", tex)
    tex = re.sub(r"\$[^$]*\$", " x ", tex)
    tex = re.sub(r"\\[a-zA-Z@]+\*?", " ", tex)
    tex = re.sub(r"[{}\[\]~\\]", " ", tex)
    count = lambda t: len([w for w in t.split() if re.search(r"[A-Za-z0-9]", w)])  # noqa: E731
    return count(tex), count(pending)


def main() -> int:
    body = pending = 0
    for name in ["introduction", "methods", "results", "discussion"]:
        w, p = words((SECTIONS / f"{name}.tex").read_text(encoding="utf-8"))
        print(f"{name:13s} {w:5d} words  (+{p} in pending notes)")
        body, pending = body + w, pending + p
    abstract = (SECTIONS / "abstract.tex").read_text(encoding="utf-8").split("\\noindent")[0]
    aw, ap = words(abstract.replace("\\section*{Abstract}", ""))
    print(f"{'BODY':13s} {body:5d} / 6000 words  (+{pending} in pending notes)")
    print(f"{'ABSTRACT':13s} {aw:5d} / 200 words  (+{ap} in pending notes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
