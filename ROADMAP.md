# Roadmap

This roadmap is the plan of record for the manuscript repository. It follows the UBC-FRESH dev
workflow. The plan for the current phases is `notes/plans/workflow-adoption-and-analysis.md`. The
roadmap before the workflow is archived in `notes/archive/roadmap-pre-workflow.md`.

## Issue Tracker Map

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P0 Workflow adoption and analysis readiness | #29 | `feature/p0-workflow-analysis` | active |
| P1 Results and manuscript | #35 | `feature/p1-results-manuscript` | active |
| P2 Submission package and data release | #37 | `feature/p2-submission` | active |

## Conventions

- A phase is `P<n>`. A task is `P<n>.<m>`. A subtask is a checklist item inside the task's issue body.
- Status values are `planned`, `active`, `pr-open`, `complete`, and `deferred`.
- A phase becomes `active` only after its parent issue exists and the maintainer approves it.
- A phase ends with a close-out report in `notes/reports/`. Merges, branch deletions, and issue
  closures happen only after the maintainer approves that report.

## Phase 0: Workflow adoption and analysis readiness

Parent issue: #29
Branch: `feature/p0-workflow-analysis`
Status: active

Goal: bring this repository under the UBC-FRESH dev workflow, make the analysis of the FHOPS 1.0.1
re-run reproducible and tested, and leave the paper ready for the results to be written.

- [ ] P0.1 Planning surfaces in workflow grammar (#30)
  - [ ] Archive the pre-workflow roadmap
  - [ ] Rewrite the roadmap, convert the changelog, and remove the home-directory paths
- [x] P0.2 Framework and gates (#31)
  - [x] Obtain the decision on ADR 0001 (D1)
  - [x] Adopt the seed framework and the `manuscript` gate (the `assets` gate lands in P0.5)
- [x] P0.3 Tests, typing, and docstrings for the analysis code (#32)
  - [x] Unit, contract, and negative-control tests for every script in `scripts/`
  - [x] `mypy --strict` and numpydoc docstrings
- [x] P0.4 Input audit of the re-run (#33)
  - [x] Audit with negative controls (`results/audit/runs_audit.csv`)
  - [x] Final audit: 232 of 232 runs pass
- [~] P0.5 Deterministic analysis pipeline (#34)
  - [x] One command regenerates every paper asset from the committed results
  - [ ] `--check` mode and the `assets` gate (deferred; needs byte-stable figures)

Detailed Next Steps Notes: the analysis is ready for the 113 SA runs and the 117 MIP runs now (D2).
The four missing SA runs are re-run JIT. The framework adoption (P0.2) waits for ADR 0001. The
analysis code is not merged until P0.3 passes.

## Phase 1: Results and manuscript

Parent issue: #35
Branch: `feature/p1-results-manuscript`
Status: active

Goal: write the Results, Discussion, Conclusions and Limitations from generated numbers only, and
finish the abstract, the introduction and the methods.

- [~] #36 P1.1 Final analysis run with all runs complete (blocked on two `sub112_lock1` SA runs)
- [x] P1.2 Analysis memo: RQ1 to RQ4, and the Ch. 4 conclusions confirmed, qualified, or revised
  (`notes/analysis/analysis-memo.md`; the two pending runs are recorded as a deviation)
- [x] P1.3 Results section from the generated macros (`manuscript/sections/results.tex`)
- [x] P1.4 Discussion, Conclusions, and Limitations (`manuscript/sections/discussion.tex`)
- [x] P1.5 Abstract, Introduction, and Methods pass (abstract 200/200; body 4612/6000; 41 refs)
- [x] P1.6 Supplement: Tables S1 and S2 rendered, S3 described as the machine-readable deposit

## Phase 2: Submission package and data release

Parent issue: #37
Branch: `feature/p2-submission`
Status: active

Goal: a submission package for CJFR, with the data released and archived, ready for G. Paradis to
submit.

- [x] P2.1 Checklist, cover letter, and flattened LaTeX source for ScholarOne
  (`scripts/package_submission.py` -> `submission/package/`)
- [~] P2.2 Data release: public repositories, GitHub releases, and Zenodo DOIs (each approved)
- [ ] P2.3 Close-out and handoff to G. Paradis
