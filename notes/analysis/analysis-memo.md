# Analysis memo: FHOPS 1.0.1 rolling-horizon re-run

Inputs: `results/rerun/runs_metrics.csv` (234 runs: 117 MIP, 117 SA — the complete grid). Size-40
full-horizon MIP baselines use the 7200 s re-runs. Every run scored on its stitched plan. Generated
by `scripts/analyze_rerun.py`.

## Headline

With state carried between windows and the stitched plan scored against the full problem, the
rolling-horizon configuration matters little. Every configuration delivers within about 4 percent
of the best plan found for its scenario. Planning horizon and lock span have small, consistent
effects; solver choice and solver time limits matter more, and they explain the few weak cells.

## RQ1: at what horizon do gains become small?

Median delivered volume relative to the best known plan, size 40, both methods, by window length
(lock span in columns):

| window (weeks) | f = 1 d | f = 7 d | f = 14 d |
|---|---|---|---|
| 2  | 0.983 | 0.983 | 0.959 |
| 4  | 0.993 | 0.992 | 0.992 |
| 8  | 0.993 | 0.992 | 0.991 |
| 16 | 0.976 | 0.984 | 0.962 |

Gains from extending the window beyond 4 weeks are negligible at 8 weeks and slightly negative at
16 weeks, where MIP windows hit the time limit often (70 percent of size-40 windows reach the
stage-1 limit). The 4- and 8-week windows are the best or tied-best in every lock span. Answer:
beyond about 4-8 weeks, the marginal gain is within noise, and at 16 weeks it is confounded by
solver tractability.

## RQ2: does frequent re-optimization beat longer windows updated less often?

Frequent re-optimization helps only mildly. Median relative volume by lock span, all sizes:
f = 1, 0.991 (SA) and 1.000 (MIP); f = 7, 0.990 and 1.000; f = 14, 0.990 and 1.000. At size 40 the
14-day lock span is 1-3 percent below the others. The 1-day and 7-day spans are indistinguishable.
So the earlier finding that re-optimization frequency dominates does not survive the corrected
procedure; only the longest lock span (14 days) shows a small, consistent penalty.

## RQ3: continuity and feasibility

All 106 SA plans are feasibility-clean in the replay (0 sequencing violations). 25 of the 117 MIP
runs show raw violations, 58 in total, but only 1 run has any at the 1e-3 m3 tolerance: they are the
negligible-production rows (UBC-FRESH/fhops#157). Continuity is descriptive only, because machine
moves are free in these scenarios: neither method is rewarded for keeping a machine on a block.
Median continuity rises with problem size and is higher for SA than MIP at 18 and 40 blocks
(size 40: SA 0.28, MIP 0.20).

## RQ4: problem size, method, and computing effort

- Delivery: size 6 saturates (both methods at 100 percent of best known). Size 18: MIP 1.000,
  SA 0.990. Size 40: MIP 1.000, SA 0.978.
- Paired SA/MIP comparison: SA beats MIP by more than 0.5 percent in 8 of 106 configurations, all
  at 40 blocks with 14- or 112-day windows, reaching 1.114 times MIP. Elsewhere MIP is at least as
  good.
- Time: median wall time for size 40 is 10.2 h (MIP) and 4.5 h (SA); for size 6, 1.8 h and 0.3 h.
  MIP reached the stage-1 time limit in 4.4, 37.9, and 70.0 percent of windows at 6, 18, and 40
  blocks; SA never did (it is iteration-bounded).
- Window failures: 9 windows returned no solution and 17 were empty, all in MIP runs at 18 and 40
  blocks. These are the weak cells in the SA/MIP comparison.

## The Ch. 4 conclusions, re-tested

| Ch. 4 claim | Verdict | Evidence |
|---|---|---|
| Re-optimization frequency dominates solution quality | Revised | Only the 14-day lock span is worse, by 1-3 percent at size 40; f = 1 and f = 7 are indistinguishable. |
| Diminishing returns beyond about 8 weeks | Confirmed, with a limit | 4- and 8-week windows are best; 16 weeks is no better and is confounded by MIP time limits. |
| Weekly re-optimization over 4-8 weeks is a practical sweet spot | Supported | Among the best configurations, and far cheaper than the 1-day lock (fewer windows). |
| Horizon length mainly drives computing effort | Confirmed | Time grows with the horizon; MIP time-limit hits grow with size. |
| Daily re-optimization gives near-identical solutions across horizons | Qualified | All horizons give 96-99 percent of best; the differences are small, not zero. |
| MIP continuity falls with horizon, SA rises | Not re-tested as such | Continuity is descriptive here; moves are free, so it is not an optimized property. |

## Deviations and limits

- All 234 runs are included (the two 112-day, 1-day-lock SA runs at 40 blocks — North Island and
  Prince George — completed on 2026-10-18 at 56.3 h and 63.6 h; they fill the size-40 16-week,
  1-day-lock cell, which moves from 97.6 to 98.2 percent of best known).
- MIP solves are time-limited, not proven optimal. The full-horizon MIP baselines are not optimal
  either (gaps up to 2.2 percent on NI at 7200 s), so relative volume near 1.0 is close to the
  resolution of the experiment.
- Size-40 MIP windows hit the time limit often; part of the 16-week penalty is a tractability
  effect, not a planning effect.
