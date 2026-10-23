# Seeded-start evidence: equal total budget on the 112-day, 40-block window

This directory holds the experiment behind the single Limitations sentence on seeded starts. It is
**not** a rolling-horizon run: it is the full-horizon operational MILP for `pg_40`, used to test
whether a heuristic seed changes what the MIP can achieve inside the per-window cap.

## Question

Does seeding the MILP from a heuristic plan (made MILP-feasible with a fixed-binary LP) let it solve
a larger instance, or reach a better plan, within the 1,800 s per-window cap?

## Design

- Instance: `pg_40` full-horizon operational MILP (112 days, 40 blocks), Gurobi 13.0.3, 36 threads,
  otherwise idle 72-core host.
- **Equal total budget**: every arm receives 1,800 s of wall clock, seed included. Seeded arms get
  `MIP limit = 1800 - seed wall - LP wall`.
- Seed sources: greedy (free), simulated annealing (108 iterations), ILS (50 iterations), tabu
  search (104 iterations). Iteration counts were calibrated to a ~1,200 s seed allowance from short
  timing probes (SA 11.06 s/iter, Tabu 11.51 s/iter; ILS 50 iterations is ~1,207 s on this instance).
- Start construction (`feasible_start`): fix every assignment binary to the plan, solve the
  resulting LP so the continuous flows/inventories/transitions are derived subject to every
  constraint, unfix, and pass the full point to the MIP as a warm start.
- `cold` receives no informed start. Pyomo passes the model's default variable initialisation as a
  "user MIP start" (objective −1.309e+06 at 0.59 s); it carries no information.
- Single seed (42).

## Result (`equal_total_pg40.jsonl`)

| arm | seed wall (s) | LP (s) | MIP (s) | total (s) | objective | MIP gap |
|---|---|---|---|---|---|---|
| cold | 0 | – | 1,827.7 | 1,827.7 | **392,699.08** | **0.7434%** |
| greedy | 10.4 | 17.2 | 1,797.5 | 1,825.0 | 391,541.56 | 1.0412% |
| SA (108 iters) | 1,133.4 | 15.9 | 674.7 | 1,823.9 | 389,954.89 | 1.4523% |
| ILS (50 iters) | 1,081.8 | 16.6 | 724.5 | 1,822.9 | 390,139.35 | 1.4043% |
| Tabu (104 iters) | 1,094.5 | 16.6 | 711.8 | 1,822.9 | 390,685.60 | 1.2626% |

Both seeded starts were verified as loaded (`Loaded user MIP start with objective …`), so the result
is not a rejected-start artefact.

## Reading

1. Cold is best or tied-best on objective and has the best gap. No seeded arm beats it.
2. The objective spread is ≤0.7%, so the honest statement is "no material quality difference", not
   "seeding hurts".
3. Seeding's measured benefit is **early feasibility**: a usable incumbent at `t ≈ 0.5 s`
   (204,034–254,042) versus cold's first improving incumbent at **410 s**.
4. Therefore seeding does **not** extend the instance size solvable within the cap, and the sentence
   in the manuscript is worded to claim early feasibility only.

## Caveats that bound the claim

- Single instance, single seed, full-horizon MILP. The paper's rolling windows add locks and carried
  state and are a different model; some of those windows failed cold in the grid. These numbers bound
  a claim about *scale*, not about those specific windows.
- **The earlier "cold is catastrophic" reading was a 300 s budget artefact.** At 300 s cold returned
  −1,309,443; at the study's 1,800 s cap it returns 392,699 with a 0.74% gap. Do not cite the 300 s
  figure as a property of the instance.
- MIP gap is `|bound − incumbent| / |incumbent|` in Gurobi. It is not comparable across arms whose
  incumbents have different signs; every final incumbent here is positive, so these are comparable.
