# Plan: adopt the UBC-FRESH dev workflow and finish the analysis and manuscript

Status: proposed for maintainer approval (see "Decisions" below). Date: 2026-10-16.
Plan of record: `ROADMAP.md`, phases P0 to P2. Governing pages: `ubc-fresh-dev-workflow`
(`docs/agents/session-protocol.rst`, `docs/agents/bounded-moves.rst`,
`docs/reference/workflow-model.rst`, `docs/reference/phase-closeout.rst`,
`docs/reference/approval-gates.rst`, `docs/reference/issue-standard.rst`,
`docs/reference/git-conventions.rst`, `docs/reference/quality-gates.rst`,
`docs/agents/green-dashboard.rst`, `docs/reference/testing-policy.rst`,
`docs/reference/github-mapping.rst`, ADR 0008 and ADR 0009 of that repository).

## 1. Where things stand (evidence, 2026-10-16)

- Re-run grid (experiment repository, `data/output/rerun_v101_gurobi/`): 117 of 117 MIP runs
  complete, none failed. 113 of 117 SA runs complete. The four missing SA runs (North Island and
  Prince George, 40 blocks, 1-day lock, 56- and 112-day windows) restarted after a host reboot on
  2026-10-15 and are still running.
- Input audit (`scripts/audit_rerun_inputs.py`, `results/audit/runs_audit.csv`): 230 of 230 runs
  pass. Each run's window count, window start days, horizon coverage, assignment row count, error
  key, and delivered volume (against a fresh deterministic replay) agree with the run's own record.
  The audit fails on each of four deliberately broken copies of a run and passes on the original
  (`notes/analysis/input-audit.md`).
- Interim MIP analysis (`results/mip_interim/`, not for the paper): merged in PR #27.
- Manuscript (`UBC-FRESH/fhops-cjfr-rolling-horizon`): skeleton, methods, introduction, supplement
  tables and the AI and CRediT statements are in place. Results and discussion are placeholders.
  The body is about 3,500 of 6,000 words. No tests exist for the analysis scripts.

## 2. Deviations from the workflow (to be cleared in P0)

| Deviation | Cause | Remedy (task) |
| --- | --- | --- |
| No parent issues, phases, or roadmap grammar; `ROADMAP.md` does not pass the validator. | The repository predates the workflow and used issue-per-task numbering. | P0.1 rewrites `ROADMAP.md` in grammar, archives the old roadmap, and mirrors P0 in a parent issue. |
| `CHANGE_LOG.md` is newest-first, with `#` headings. The validator requires `##` ISO dates, newest last. | Older convention. | P0.1 converts the file in place. No entry is removed or rewritten. |
| Personal home-directory paths in `AGENTS.md` and `notes/cjfr-guidelines.md`. | Written during setup. | P0.1 replaces them with placeholders. |
| No framework: no validator, dashboard, lint, type, or test configuration, and no pre-commit. | Not adopted before now. | P0.2 adopts it after the gate decision (ADR 0001). |
| Analysis scripts (`analyze_rerun.py`, `make_table_scenarios.py`, `make_supplement_tables.py`, `wordcount.py`, `audit_rerun_inputs.py`) have no tests and incomplete type annotations and docstrings. | Written as one-off scripts, outside the workflow. | P0.3 adds tests, strict typing and numpydoc docstrings. The analysis is not merged until P0.3 passes. |
| Interim analysis (PR #27) was merged without tests. | Same as above. | Covered by P0.3, and its outputs stay gitignored until P1. |
| Work on the analysis started before its phase was active. | Phase P0 did not exist. | Disclosed here. The audit was run as read-only validation and is recorded as P0.4 evidence. |
| The first commit of this phase cannot leave the dashboard green, because no dashboard exists yet. | The framework is adopted in P0.2. | Disclosed in the P0.1 closeout comment. P0.2 restores green before any merge. |

## 3. Phases and tasks

### P0: Workflow adoption and analysis readiness (active)

Acceptance: the validator passes on the repository. The dashboard is green on the phase
branch. Every script in `scripts/` has tests and passes `mypy --strict`. The audit passes for
all runs, and the final audit is recorded after the four SA runs complete. The analysis pipeline
regenerates every paper asset from `results/`.

- P0.1 Planning surfaces in workflow grammar. Roadmap and changelog rewritten, personal paths
  removed, pre-workflow roadmap archived. Validator findings for these files are zero, except
  findings that P0.2 is meant to clear.
- P0.2 Framework and gates. ADR 0001 (proposed) records the gate set. Seed framework adopted:
  `scripts/check_workflow.py`, `scripts/dashboard.py`, `pyproject.toml`, `requirements-dev.txt`,
  `.pre-commit-config.yaml`, the docs skeleton and CI workflows. The gate set is a maintainer
  decision (see section 4).
- P0.3 Tests, typing, and docstrings for the analysis code. Every function in `scripts/` gets
  unit tests, with failure paths. Branch coverage is at least 95 percent. Negative controls
  (deliberately broken inputs) back every check in the audit.
- P0.4 Input audit of the re-run. 230 of 230 runs pass (done for the 113 SA and 117 MIP runs
  present on 2026-10-16). Final audit, with the four SA runs, after they complete.
- P0.5 Deterministic analysis pipeline. One command regenerates `results/`, the tables, the
  figures, and `numbers.tex` from the run outputs. The interim outputs are removed from
  `manuscript/`. The figures pass a visual check (legends, units, axis limits).

### P1: Results and manuscript (planned)

Acceptance: the Results, Discussion and Conclusions are written from generated macros only.
No `\pending{}` remains in the body. The body is within the CJFR limit, and the abstract is
within 200 words. Every cited reference resolves.

- P1.1 Final analysis run, after the four SA runs complete. Re-run the audit and the pipeline.
  Record the head commit, the audit result, and the assets' hashes in the changelog.
- P1.2 Analysis memo. Answers RQ1 to RQ4, and states each Ch. 4 conclusion as confirmed,
  qualified, or revised, with the number that decides it. Written for G. Paradis's sign-off.
- P1.3 Results section, from the macros in `manuscript/generated/numbers.tex`.
- P1.4 Discussion, Conclusions and Limitations.
- P1.5 Abstract, Introduction and Methods pass. Word budget and reference check
  (`scripts/wordcount.py`, a resolution check for every `\cite`).
- P1.6 Supplement: Tables S1 and S2 (already generated) and Table S3 (the per-run table).

### P2: Submission package and data release (planned)

Acceptance: the checklist has no open items except those that need the submitter. The data
repositories and their DOIs exist, with the approvals that the approval gates require.

- P2.1 Checklist, cover letter, and a flattened LaTeX source package for ScholarOne.
- P2.2 Data release. Make both repositories public, cut the GitHub releases that trigger the
  Zenodo archive, and insert the DOIs. Each of these is a separate approval (see section 5).
- P2.3 Close-out and handoff to G. Paradis, who submits. The AI-use statement and the CRediT
  statement are re-checked at ScholarOne entry.

## 4. Decisions, with recommended defaults

| # | Decision | Recommended default | Why |
| --- | --- | --- | --- |
| D1 | Gate set for this repository (ADR 0001). | Seed gates (lint, format, types, tests with the coverage gate, validator, docs), plus two project gates: `manuscript` (tectonic builds of the paper, cover letter and supplement, with no undefined references) and `assets` (regenerating the paper assets from `results/` leaves no diff). | The paper is LaTeX and the numbers are generated. A green dashboard should mean that the paper matches its results. |
| D2 | Which SA and MIP results analysed now. | Analyse the 113 SA runs now as interim. Re-run the final analysis when the four SA runs finish. | The four missing runs are the slowest 40-block daily cases. Waiting for them stalls the memo, the Results, and the Discussion for days. |
| D3 | Size-40 full-horizon baselines. | 7200 s for all three areas (already applied). The 1800 s grid records go in the supplement. | Symmetry across areas. The North Island baseline is empty at 1800 s. |
| D4 | Relative-delivered reference. | Best known plan across all runs (MIP and SA) for relative delivered volume, and the same-method full-horizon baseline as a second column. | The baselines are not optimal (gaps up to 2.2 percent), so a single reference would mislead. |
| D5 | Sequencing-violation count. | Report the raw count and the count at a 1e-3 m3 tolerance. Headline the second. | Raw counts include negligible-volume rows that FHOPS replays as violations. |
| D6 | Phase activation. | P0 active now, on the maintainer's instruction of 2026-10-16. P1 and P2 activate at the close-out of the phase before them. | Approval gates. The instruction covers starting the analysis and following the workflow. |

## 5. Approval gates and external actions

Allowed without a further approval: branches, commits to the phase branch, issues and comments of
P0 to P2, local checks, notes and reports. Ask first: creating labels in the repository (the
`phase` and `task` labels are needed by the issue standard), squash-merging, closing parent
issues, deleting branches, changing repository visibility, creating tags and releases, making
the data repositories public, and creating a Zenodo deposit. Each external action is named in
the phase close-out with its exact command.

## 6. Risks

- The four missing SA runs may take longer than the estimate, because they restart from zero
  and are the slowest runs of the grid. Mitigation: D2.
- The analysis code changes after the memo is written. Mitigation: P0.5 makes the pipeline
  deterministic, and P1.1 re-runs it before any text is final.
- The gate set may grow in the dashboard run time. Mitigation: keep the audit and the replays
  as separate, optional gates, and keep the unit tests fast.
- Host restarts clear `/tmp`. Mitigation: environments and tools live under the home directory
  (`~/venvs/fhops101-grb`, `~/bin/tectonic`), and the runs are resumable.
