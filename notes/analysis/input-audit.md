# Input audit of the FHOPS 1.0.1 re-run

Status: complete for the runs present on 2026-10-16. Final audit to repeat after the four SA runs
finish (P0.4, P1.1). Script: `scripts/audit_rerun_inputs.py`. Output: `results/audit/runs_audit.csv`.

## What is checked, per run

1. Window count equals `ceil(master_days / lock_days)` for rolling runs, and 1 for baselines.
2. Window start days advance by the lock span (rolling runs).
3. The last window reaches the horizon end.
4. The run carries no `error` key.
5. `n_locked_assignments` equals the row count of the assignments CSV.
6. The saved delivered volume equals a fresh deterministic replay of the same assignments
   (`fhops.evaluation.metrics.kpis.compute_kpis`), to a relative tolerance of 1e-6.

## Result

Command: `~/venvs/fhops101-grb/bin/python scripts/audit_rerun_inputs.py --workers 8` (16 s).

| Solver | Baseline | Runs | Passed |
| --- | --- | --- | --- |
| MIP (Gurobi) | no | 108 | 108 |
| MIP (Gurobi) | yes | 9 | 9 |
| SA | no | 104 | 104 |
| SA | yes | 9 | 9 |

Total: 230 of 230. The run set is the paper set: grid runs, with the three size-40 MIP baselines
taken from the 7200 s folders.

## Negative controls

The audit must be able to fail. Four copies of `ka_6_sub14_lock7_mip.json` were broken on purpose,
and each was audited against the original assignments:

| Case | Change | Result |
| --- | --- | --- |
| control | none | passed |
| drop_window | last window removed | failed: "windows 15 != 16; last window does not reach the horizon end" |
| bad_row_count | `n_locked_assignments` + 1 | failed: "341 != 340" |
| bad_delivered | delivered volume + 1 percent | failed: replayed 30913.36 != saved 31222.49 |
| error_key | `error` added | failed: "run carries an error" |

## Limits

- The audit checks consistency between a run's record and its assignments. It does not check
  whether the MIP or SA plan is a good plan. That is what the analysis measures.
- The replay is FHOPS's own playback. A bug in playback would pass the audit. The sequencing
  violations are counted separately (`analyze_rerun.py`).
- Runs still in progress are excluded by construction.
