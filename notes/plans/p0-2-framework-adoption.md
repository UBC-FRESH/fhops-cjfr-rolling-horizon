# P0.2 framework adoption: the list, and the order

Source: the seed rendered with `python scripts/new_project.py --name "FHOPS CJFR Rolling Horizon"
--slug fhops-cjfr-rolling-horizon --owner UBC-FRESH` at `ubc-fresh-dev-workflow` commit `93b5cd9`,
written to a scratch directory outside this repository. The rendered tree has 32 files.

## Adopt as rendered (framework)

- `scripts/check_workflow.py`, `scripts/dashboard.py`
- `pyproject.toml` (ruff, mypy strict on `scripts`, `tests`, `docs/conf.py`; pytest coverage gate of
  95 percent branch coverage on `scripts`)
- `requirements-dev.txt`, `.pre-commit-config.yaml`
- `.github/ISSUE_TEMPLATE/phase.md`, `.github/ISSUE_TEMPLATE/task.md`
- `.github/workflows/ci.yml`, `.github/workflows/docs.yml`
- `notes/adr/0000-template.md`, `notes/reports/phase-closeout-template.md`
- `tests/conftest.py`, `tests/test_check_workflow.py`, `tests/test_dashboard.py`,
  `tests/test_cli.py`, `tests/test_properties.py`, `tests/test_workflow.py`,
  `tests/test_api_docstrings.py`

## Adapt (framework file, project content)

- `docs/conf.py`, `docs/index.rst`, `docs/llms.txt`, `docs/requirements.txt`, `docs/api/*.rst`.
  The index describes the manuscript and its analysis; `llms.txt` lists the project pages only.
- `notes/README.md`: the seed's index, with this repository's notes listed.
- `CONTRIBUTING.md`: the seed's text, with this repository's public-safety notes.

## Merge, keeping project content

- `AGENTS.md`: the seed's sections, adopted in full, with a project section at the end for the
  manuscript and analysis rules that are already in this file (generated assets, no Chapter 4 numbers,
  author list, AI-use declarations, and the read-only sources).
- `README.md`: the seed's reading paths, with this repository's build commands.
- `.gitignore`: the seed's entries, plus this repository's `results/*interim*/`,
  `manuscript/*/*_interim*`, `*_smoke.*`, and `tmp/` entries.

## Keep (not in the seed, or ours)

- `ROADMAP.md`, `CHANGE_LOG.md` (already in grammar; P0.1).
- `notes/` (plans, analysis, ADRs 0001, archive), `results/`, `manuscript/`, `scripts/` analysis
  scripts (`analyze_rerun.py`, `audit_rerun_inputs.py`, `make_table_scenarios.py`,
  `make_supplement_tables.py`, `wordcount.py`).

## Project gates to add to `scripts/dashboard.py` (ADR 0001)

- `manuscript`: `tectonic -o build main.tex`, then `supplement.tex` and `cover-letter.tex` from
  `submission/`, with zero errors and zero undefined references or citations in the logs. The
  tectonic path comes from `TECTONIC`, defaulting to `tectonic` on `PATH`.
- `assets`: `python scripts/analyze_rerun.py --check`, which regenerates the paper assets from the
  committed results and fails on any difference. `--check` is added in P0.5.

## Order, and why

1. P0.3 first: tests, types and docstrings for every script in `scripts/`. The rendered
   `pyproject.toml` makes `mypy --strict` and the 95 percent coverage gate part of every run, so the
   analysis scripts must pass them before the framework lands.
2. P0.2 second: the framework commit, with the project gates, in one commit that leaves the
   dashboard green. The workflow forbids a red commit, so the framework is never committed without
   the tests it needs.

## Risks

- CI needs a pinned `tectonic` to run the `manuscript` gate. The CI step installs a fixed version,
  to be decided with the maintainer.
- The seed's `test_workflow.py` and `test_api_docstrings.py` may check text this repository does not
  have. Any change to those tests is recorded in the changelog with its reason, and no test is
  deleted or skipped.
