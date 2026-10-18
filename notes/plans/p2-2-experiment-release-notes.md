# Draft release notes — UBC-FRESH/jaffray-masc-fhops-model, FHOPS 1.0.1 re-run

Use as the GitHub release body when the outputs are published (after P1.1 completes the grid).

## FHOPS 1.0.1 rolling-horizon re-run (issue #1)

The complete re-run of the Chapter 4 rolling-horizon grid on **FHOPS 1.0.1**, which carries
operational state between rolling-horizon windows. Every run is scored on its stitched plan,
replayed against the full 112-day problem. These outputs supersede the Chapter 4 numbers, which came
from FHOPS 1.0.0a2 (no carry-forward, last-window objective) and are not reproducible.

### Contents

- `scripts/rolling_rerun_v101.py` — the runner (SA 500 iterations, seed 42; MIP Gurobi 13.0.3,
  1800 s stage 1 + 900 s earliness per window; 36 MIP + 34 SA workers).
- `data/input/scenarios/` — the nine case-study bundles (ka/ni/pg × 6/18/40 blocks, 112 days).
- `data/output/rerun_v101_gurobi/` — per-run JSON summaries, stitched assignment tables, Gurobi
  solver logs, and `summary.csv`; `manifest*.json` records the grid and the FHOPS provenance.
- `notes/rolling_rerun_v101.md` — decisions and evidence.

### Grid

Nine scenarios × 4 planning horizons (2, 4, 8, 16 weeks) × 3 re-optimization intervals (1, 7, 14
days) × 2 methods (SA, MIP) = 216 rolling runs, plus 18 full-horizon baselines = 234 runs.

### Headline

Almost every configuration delivers within about 4% of the best plan for its scenario; solver
behaviour, not configuration, explains the weak cases. The earlier "re-optimization frequency
dominates quality" finding does not survive the corrected procedure.

### Provenance

- FHOPS 1.0.1 (PyPI, tag v1.0.1); highspy 1.15.1; Gurobi 13.0.3; Pyomo 6.10.1.
- Hardware: 36 physical / 72 logical cores, 754 GB RAM.
- Manuscript and analysis: UBC-FRESH/fhops-cjfr-rolling-horizon.
