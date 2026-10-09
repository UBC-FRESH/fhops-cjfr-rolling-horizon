# Coding Agent Operating Notes (FHOPS rolling-horizon CJFR manuscript)

This repository holds the manuscript for the *Canadian Journal of Forest Research* (CJFR) research
article derived from Chapter 4 of Rosalia Jaffray's MASc thesis (`jaffray2026thesis`, UBC, April
2026): rolling-horizon machine scheduling with FHOPS, **re-run on FHOPS 1.0.1**. Treat this file as
the root `AGENTS.md`; it applies to all subdirectories. It follows the conventions of
`UBC-FRESH/fhops-manuscript`.

## Non-negotiables
- **Never edit on `main`, and never leave work uncommitted.** Work happens on an issue branch
  (`issue-<number>-<short-slug>`), is committed in small steps, pushed, and merged by PR.
- **Read before acting:** this file, `ROADMAP.md`, the latest `CHANGE_LOG.md` entries and
  `notes/ch4-to-cjfr-map.md`.
- **No silent changes:** record every change set in `CHANGE_LOG.md` (newest first, dated), with
  the exact commands run.
- **No Chapter 4 numbers.** The thesis Chapter 4 results were produced with FHOPS 1.0.0a2, which
  carried no state between rolling-horizon windows, and were scored by the last window's
  objective. They are not publishable. Every number in this paper must trace to a committed result
  file of the FHOPS 1.0.1 re-run (`UBC-FRESH/jaffray-masc-fhops-model`, `data/output/rerun_v101/`,
  issue #1 there) through a committed script.
- **Generated assets are never hand-edited.** Tables and figures under `manuscript/figures/` and
  `manuscript/tables/` are produced by `scripts/`; fix the script or its input and regenerate.
- **Author list:** Rosalia Jaffray, Kathleen Coupland, Gregory Paradis (corresponding). Do not
  change it without instruction from G. Paradis. All authors sign off before submission, including
  on any conclusion that differs from Chapter 4.

## Repository layout
| Path | Purpose |
|------|---------|
| `manuscript/` | LaTeX source: `main.tex`, `sections/`, `references.bib`, `figures/`, `tables/`. |
| `scripts/` | Figure/table generators reading the re-run `summary.csv` (and per-run JSON). |
| `results/` | Committed copies of the result files the paper cites (with provenance). |
| `notes/` | Living notes: thesis-to-paper map, CJFR checklist, open questions. |
| `submission/` | Cover letter and the CJFR submission checklist. |

## Read-only sources (never modify)
- Thesis: `/home/gep/projects/jaffray-rosalia-masc-thesis` (Ch. 4: `body_chapters/chap_4/`).
- FHOPS: `/home/gep/projects/fhops` (main checkout, user work) and `/home/gep/projects/fhops-v101`.
- SoftwareX paper: `/home/gep/projects/fhops-manuscript`.
- Earlier T&F-template draft: `UBC-FRESH/jaffray-masc-modelling-paper` (private, Overleaf-synced).

## Build
```
cd manuscript && /tmp/opencode/tex/tectonic -o build main.tex
```
CJFR format: double-spaced, single column, page and continuous line numbers, Letter paper,
Harvard (author year) citations, abstract ≤ 200 words, ≤ 6000 words Introduction–Discussion,
≤ 50 references.

## Workflow
- Issue → branch → PR → squash merge (subject ends in `(#<PR>)`). Update `ROADMAP.md` checkboxes
  and `CHANGE_LOG.md` in the same PR.
- Git identity (repo-local): `Gregory Paradis <0@01101.io>`.
- FHOPS bugs found while working: open an issue in `UBC-FRESH/fhops`, note it here, and continue
  unless it invalidates the experiment.
- Never print secrets.
