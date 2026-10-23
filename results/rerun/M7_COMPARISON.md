# M7 cold-MIP re-run: what changed and how the paper uses it

## Why it was run

The original grid ran the simulated-annealing and MIP phases against each other on a shared host, so
the MIP occasionally competed for CPU. `jaffray-masc-fhops-model#1` (M7) asked for the cold-start
MIP arm to be re-run **alone** so the reported time-limit hits and failures could not be attributed
to that competition.

## What was run

- `scripts/rolling_rerun_v101.py --mip-solver gurobi --solvers mip --mip-earliness-time-limit 900
  --mip-workers 36 --out-root data/output/rerun_v101_gurobi_alone`
- 117 MIP runs (108 rolling configurations + 9 full-horizon baselines), same specs as the grid:
  1,800 s stage 1, 900 s earliness stage, one Gurobi thread per window, 36 windows in parallel.
- The SA arm was not re-run; the 117 SA runs from the original grid are used unchanged.

## How the paper set was assembled

The analyser expects both methods in one directory, so a merged view was built from symlinks:

```bash
cd ../jaffray-masc-fhops-model/data/output
mkdir -p rerun_v101_m7/runs
for f in rerun_v101_gurobi/runs/*_sa.json rerun_v101_gurobi/runs/*_sa.log \
         rerun_v101_gurobi/runs/*_sa_assignments.csv; do
  ln -s "$PWD/$f" rerun_v101_m7/runs/
done
for f in rerun_v101_gurobi_alone/runs/*; do ln -s "$PWD/$f" rerun_v101_m7/runs/; done
# summary.csv = SA rows from the grid + MIP rows from the re-run (117 + 117)
```

then

```bash
python scripts/analyze_rerun.py --rerun-dir ../jaffray-masc-fhops-model/data/output/rerun_v101_m7
```

`rerun_v101_m7/` is a working view only (symlinks); it is not committed.

## What changed

Per-run comparison: `m7_rerun_comparison.csv` (117 MIP runs, old vs re-run).

| quantity (all 117 MIP runs, raw summary) | original | re-run |
|---|---|---|
| windows with no solution | 9 | **32** |
| empty windows | 18 | **39** |
| total delivered volume (m³) | 42,488,312 | 42,191,374 |

Paper-set macros (108 rolling MIP runs, after playback): no-solution windows 9 → 32, empty windows
17 → 38, runs more than 4% short 16 → 22 of 216, SA-winning pairs 9 → 16 of 108.

20 of the 117 runs changed their window outcomes; the rest are identical.

## Why this is not a contention artefact

Matching 603,700 per-solve Gurobi records from the two runs: the re-run's work rate is **8.4%
higher** (median 0.523 → 0.567 work units per second; mean 0.562 → 0.586). The re-run had, if
anything, more solver throughput — and still produced more failures.

## Interpretation

The failure counts are a property of a **time-limited** solve, not of the instance. A different
incumbent found inside 1,800 s changes the state carried into the next window, which cascades: that
is why 20 long (`lock1`) trajectories diverge while short ones are unaffected. The paper's
Limitations sentence states this explicitly and does not claim a direction for the original
contention.

## Consequence for the paper

The re-run is the reported basis: it is the commissioned run and the better-resourced one. The
conclusions are unchanged in direction — most 40-block windows still hit the stage-1 limit (66.7%,
was 70.0%), the worst rolling run is still ~12% short (88.0%, was 87.9%), and SA still never fails —
but the failure counts are larger and the text quotes the re-run's macros.
