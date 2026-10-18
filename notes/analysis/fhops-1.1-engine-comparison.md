# Does FHOPS 1.1 change the paper's results? (engine comparison, 2026-10-18)

Question: the paper's SA grid was produced on FHOPS 1.0.1. The merged FHOPS 1.1 line
(`main`, `39b3744`) adds the P9/P10 performance work (behaviour-identical), the ADR-0003 bounded
`cross_exchange` sampling (changes the SA stream), and an opt-in adaptive cooling schedule (off).
Would re-running the grid on 1.1 give materially different results?

## Method

Re-ran selected SA grid specs with the experiment runner
(`jaffray-masc-fhops-model/scripts/rolling_rerun_v101.py`, 500 SA iterations, seed 42) under both
engines, into separate output roots. A 1.0.1 control re-ran 6 size-6 specs and reproduced the banked
delivered volumes **exactly** (6/6), validating the comparison. Banked values are the committed
`results/rerun/runs_metrics.csv`.

## Result

| run | wall 1.0.1 (s) | wall 1.1 (s) | speedup | delivered-volume delta |
|---|---|---|---|---|
| ka_6_baseline_sa | 63.2 | 17.1 | 3.7x | 0.000% |
| pg_6_baseline_sa | 81.7 | 18.7 | 4.4x | 0.000% |
| ka_6_sub14_lock14_sa | 52.5 | 26.1 | 2.0x | 0.000% |
| pg_6_sub14_lock14_sa | 68.3 | 27.5 | 2.5x | 0.000% |
| ka_6_sub28_lock14_sa | 95.4 | 56.9 | 1.7x | 0.000% |
| pg_6_sub28_lock14_sa | 118.5 | 50.9 | 2.3x | 0.000% |
| ka_18_sub14_lock14_sa | 384.4 | 81.5 | 4.7x | 0.000% |
| ni_18_sub14_lock14_sa | 1143.3 | 82.2 | 13.9x | -0.294% |
| ni_18_sub14_lock7_sa | 2263.5 | 164.1 | 13.8x | -0.147% |
| ni_18_sub28_lock14_sa | 2630.4 | 160.1 | 16.4x | +0.147% |
| pg_18_sub14_lock14_sa | 1172.2 | 80.9 | 14.5x | -0.149% |
| pg_18_sub14_lock7_sa | 2412.8 | 160.6 | 15.0x | +0.149% |
| pg_18_sub28_lock14_sa | 2449.5 | 156.5 | 15.7x | 0.000% |

- Speed: median 2.4x at size 6, **14.5x at size 18**; the gain grows with scenario size because the
  P10 work scales with the per-move repair cost.
- Quality: identical where the scenario saturates; otherwise |delta| <= 0.29%, signed both ways.
  Consistent with a different-but-equivalent trajectory from the ADR-0003 stream change, not a
  systematic gain or loss. Sequencing violations: 0 in both.

## Conclusion

FHOPS 1.1 runs the same search **much faster** and is **not materially better or worse**. Re-running
the grid on 1.1 would not change any paper number; it would only reduce wall time (the banked
115-run SA grid is 413.6 h; size 6 31.5 h, size 18 118.0 h, size 40 264.1 h). The manuscript keeps
its FHOPS 1.0.1 provenance. The 1.1 speedup is a software-release note, not a manuscript result.

Only sizes 6 and 18 were tested; size-40 quality is inferred (its speedup should be >= size 18).
