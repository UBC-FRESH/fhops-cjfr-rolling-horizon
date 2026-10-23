# Phase close-out report: P1 Results and manuscript

Phase: P1, Results and manuscript
Parent issue: #35
Pull request: #38, `feature/p1-results-manuscript` into `main`
Evidence head: the tip of `feature/p1-results-manuscript` at approval time
Report commit: the commit that adds this report. Its CI run is posted on the pull request.
Date: 2026-10-18
Status: queued for approval. Not merged.

## Recommendation

Approve these actions. The agent carries them out in this order, and reads back each result.

1. Merge pull request #38 and delete the branch `feature/p1-results-manuscript`.
2. Close parent issue #35 and child #36, and also close the P0 issues **#29–#34** and #28 (this
   branch carries the never-merged P0 work), each with a closeout comment citing the merge commit.
3. Keep P2 (#37) open: its data release is in flight and its close-out is a separate report.

Settings changes, each with its exact command. Each one runs only after its own approval.

- Re-cut the manuscript release after the merge (see "Release" below):
  `gh release create v1.0.1 -R UBC-FRESH/fhops-cjfr-rolling-horizon --target main --title "CJFR submission v1.0.1" --notes-file <notes>`

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| P1.1 final analysis with all runs complete | `results/rerun/runs_metrics.csv` = 234 runs (117 MIP + 117 SA); audit 234/234 | met |
| P1.2 analysis memo (RQ1–RQ4, Ch. 4 re-test) | `notes/analysis/analysis-memo.md` | met |
| P1.3 Results from the generated macros | `manuscript/sections/results.tex` | met |
| P1.4 Discussion, Conclusions, Limitations | `manuscript/sections/discussion.tex` | met |
| P1.5 abstract/intro/methods pass | abstract 200/200; body 4,562/6,000; 42 refs | met |
| P1.6 supplement S1–S3 | `manuscript/supplement.tex` (S1–S2 rendered; S3 described) | met |
| Every quoted number is a macro | `manuscript/generated/numbers.tex`; no `\pending{}` remains | met |
| Authors sign off on any conclusion differing from Ch. 4 | `manuscript/sections/discussion.tex` Table 4 | author action, pending |

## 2. Workflow compliance

- Parent issue #35 before the branch; child #36 opened and linked as a sub-issue.
- The branch was cut from the P0 tip (`feature/p0-workflow-analysis`), not from `main`, because P0
  was never merged — see the deviations.
- Commit messages start with the task IDs (`P1.1`, `P1.2`, …) for the P1 commits.
- `ROADMAP.md` and `CHANGE_LOG.md` updated with each task.
- Gates run before this report: dashboard GREEN (lint, format, types, tests, validator, docs,
  manuscript).
- Approval gates: this report; the merge, the branch deletion, and the issue closures run after
  approval.

## 3. Gate evidence

```
GATE                STATUS   SECONDS
lint                GREEN
format              GREEN
types               GREEN
tests               GREEN   (97.8% coverage)
validator           GREEN   (0 errors, 0 warnings)
docs                GREEN
manuscript          GREEN
OVERALL: GREEN
```

- Input audit: `python scripts/audit_rerun_inputs.py --workers 8` -> **234 audited, 234 passed**.
- Build: `cd manuscript && tectonic -o build main.tex` and `... supplement.tex` (0 errors).
- Words: body 4,562/6,000; abstract 200/200.

## 4. Deviations and risks

- **The branch bundles P0 and P1 (and P2.1).** `main` is far behind; the P0 phase was never merged,
  so the P1 branch inherits it. One PR therefore delivers the workflow framework (P0), the
  manuscript (P1), and the submission package (P2.1). Splitting would require rebasing P0 onto
  `main` first; the single PR is the pragmatic choice and this report names it.
- **`main` and the branch had diverged** by one commit (AGENTS.md environment paths, #28); it was
  merged into the branch, resolving the AGENTS.md conflict in favour of the public-facing build
  commands.
- **Data release (P2.2) is not finished.** Its DOIs (analysis-release pending) and the author
  sign-off are the remaining submission blockers, tracked under P2 (#37).
- The paper reports the single-seed SA trajectory, not a distribution (stated in Limitations).

## 5. Release

- Today's `v1.0.0` release captured the 115-run analysis; the final numbers warrant a `v1.0.1`
  release after the merge (it also gives Zenodo a fresh version DOI). Named above for approval.
