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
  file of the FHOPS 1.0.1 re-run (`UBC-FRESH/jaffray-masc-fhops-model`,
  `data/output/rerun_v101_gurobi/`, issue #1 there) through a committed script
  (`scripts/analyze_rerun.py` → `results/rerun/`, `manuscript/tables/`, `manuscript/figures/`,
  `manuscript/generated/numbers.tex`). Quote numbers in the text through the generated macros.
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
| `notes/` | Living notes: thesis-to-paper map (`ch4-to-cjfr-map.md`), CJFR rules (`cjfr-guidelines.md`), `open-questions.md`. |
| `submission/` | Cover letter and the CJFR submission checklist. |

## Read-only sources (never modify)
- Thesis: `/home/gep/projects/jaffray-rosalia-masc-thesis` (Ch. 4: `body_chapters/chap_4/`).
- FHOPS: `/home/gep/projects/fhops` (main checkout, user work) and `/home/gep/projects/fhops-v101`.
- SoftwareX paper: `/home/gep/projects/fhops-manuscript`.
- Earlier T&F-template draft: `UBC-FRESH/jaffray-masc-modelling-paper` (private, Overleaf-synced).

## Build
```
python scripts/make_table_scenarios.py          # Table 1 (scenario bundles)
python scripts/make_supplement_tables.py        # Tables S1-S2 (calibration, solver probe)
python scripts/analyze_rerun.py                 # results/rerun, Tables 2-3, Figs. 2-3, numbers.tex
scripts/build_figures.sh                        # Fig. 1 (TikZ)
cd manuscript && ~/bin/tectonic -o build main.tex && ~/bin/tectonic -o build supplement.tex
python scripts/wordcount.py                     # CJFR limits
```
Python: the FHOPS 1.0.1 venv (`~/venvs/fhops101-grb (fhops 1.0.1 + matplotlib)`, plus matplotlib). Assets with a
`_smoke` suffix come from the smoke run and are for pipeline testing only; never cite them.
CJFR format: double-spaced, single column, page and continuous line numbers, Letter paper,
Harvard (author year) citations, abstract ≤ 200 words, ≤ 6000 words Introduction–Discussion,
≤ 50 references.

## AI-use declarations
- Follow the target journal's rules exactly. CSP/CJFR requires every AI-assisted tool to be
  disclosed with its name and model/version: writing assistance in the Acknowledgements, research
  and code use in the Methods, and again in ScholarOne. This paper names Claude Opus 5.5
  (Anthropic, via OpenCode) for experiment code and text, Kimi K3 for the original rolling-horizon
  runner, and OpenAI GPT-5.x (several versions) for FHOPS design, implementation and testing
  (G.P., 2026-10-10). Ask about the tools behind any new code before submission.
- G.P.'s preference, where a journal allows it, is a generic declaration: "LLM coding and writing
  agents were used at various stages", with use-case examples and no vendor or model names.
- Either way the statement must be truthful: it covers every kind of use, and the authors actually
  review what it says they reviewed.

## Workflow
- Issue → branch → PR → squash merge (subject ends in `(#<PR>)`). Update `ROADMAP.md` checkboxes
  and `CHANGE_LOG.md` in the same PR.
- Git identity (repo-local): `Gregory Paradis <0@01101.io>`.
- FHOPS bugs found while working: open an issue in `UBC-FRESH/fhops`, note it here, and continue
  unless it invalidates the experiment.
- Never print secrets.
