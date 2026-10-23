# Thesis Ch. 4 → CJFR manuscript map

Source: `jaffray-rosalia-masc-thesis/body_chapters/chap_4/chap_4.tex` (read-only).
Fates: **kept** (little change), **rewritten** (content kept, text redone), **dropped**,
**pending re-run** (claim must be re-tested on FHOPS 1.0.1 before it can appear).

| Ch. 4 section / claim | Fate | Where / note |
|---|---|---|
| §4.1 Intro: forest ops complexity, delays, uncertainty (Martell; D'Amours; Alayet; Arora) | rewritten | Introduction ¶1 |
| §4.1 Practice ranges from whiteboards to proprietary tools; fragmented progress (jaffray2025systematic) | rewritten | Intro ¶1. The systematic review is now **published** (Jaffray, Coupland, Paradis 2026, *International Journal of Forest Engineering*, DOI 10.1080/14942119.2026.2662184) and is cited directly as `jaffray2026systematic`. |
| §4.1 Large combinatorial problems; rolling horizon as remedy (Bellavenutte; Sethi; Venkataraman; Feng) | rewritten | Intro ¶2 |
| §4.1 Horizon length / re-optimization frequency theory (Baker; Santos; Sethi; Chand) | rewritten | Intro ¶3 |
| — (new) carry-forward and stitched-plan evaluation as preconditions of a valid evaluation | new | Intro ¶4, Methods §2.3, Discussion §4.2 |
| §4.1 RQ1 (horizon with diminishing gains) | kept | RQ1, now about delivered volume |
| §4.1 RQ2 (stable θ × f combinations) | rewritten | Merged into RQ3 (continuity + feasibility) |
| §4.1 RQ3 (different horizons converge to similar solutions?) | dropped as separate RQ | Covered descriptively under RQ1. Could be revived with a plan-similarity metric if needed. |
| §4.1 RQ4 (frequent re-optimization vs longer windows) | kept | RQ2 |
| — (new) RQ4: problem size, solver choice, computing time | new | Replaces the thesis's solver-performance narrative |
| §4.2.1 Study design, FHOPS, Pyomo/HiGHS, SA 500 iters, seed fixed | rewritten | Methods §2.2. FHOPS 1.0.1; MIP on Gurobi (1800 s + 900 s earliness), justified by the calibration (Table S1) and the HiGHS comparison (Table S2). |
| §4.2.1 "FHOPS (v1.0.0), HiGHS 1.13.1, Pyomo 6.10.0" | dropped | Re-run uses FHOPS 1.0.1, highspy 1.15.1 / Gurobi 13.0.3, Pyomo 6.10.1 |
| §4.2.1 rolling definition (θ, f_roll) | rewritten | Methods §2.3 with carry-forward steps |
| §4.2.1 Hardware "72 CPU cores, 768 GB" | rewritten | 36 physical / 72 logical cores, 754 GB; 36 MIP + 34 SA workers (Methods §2.4) |
| §4.2.2 Data inputs (FHA, VRI, DEM slope) | kept | Methods §2.1 |
| §4.2.3 Dataset table (blocks/machines) | rewritten | Table 1, generated from the scenario bundles (`scripts/make_table_scenarios.py`) with volumes, slopes, stem sizes |
| §4.2.4 Factorial design; "108 runs" | rewritten | 216 runs (×2 methods) + 18 baselines |
| §4.2.5 KPIs: objective deviation vs benchmark | dropped/rewritten | Replaced by stitched-plan delivered volume relative to a reference. The last-window objective is invalid. |
| §4.2.5 Continuity (Vanhoucke 2006 definition) | kept (pending re-run) | Recomputed from the stitched assignments of the re-run |
| §4.2.5 Computational metrics (runtime, time-limit fraction) | kept (pending re-run) | Plus per-window status counts (no_solution / empty / skipped) |
| §4.2.6 Reproducibility (Zenodo dataset, open stack) | rewritten | Data availability statement. Run outputs to be deposited (Dryad/Zenodo). |
| §4.3 All numbers (runtimes 617/3411 s, deviations 3–23 %, 60–98 %, 20 %→12 %, continuity 0.281→0.058, 0.383/0.112/0.078, ">80 % time-limited") | dropped | Not publishable (no carry-forward; last-window metric) |
| §4.3 "Largest horizon solved to optimality: 16/8/2 wk" | pending re-run | Old model; re-test with FHOPS 1.0.1 status data |
| §4.3 MIP 1–2 orders of magnitude slower than SA | pending re-run | Likely to hold; must come from new wall times |
| Conclusion: re-optimization frequency dominates quality | pending re-run | Pre-fix smoke suggests the lock-span effect was largely an artifact (ka_6 sub14/lock7 MIP: 7896 m³ / 13 violations pre-fix vs 30913 m³ / 0 post-fix). Discussion §4.1 (a). |
| Conclusion: diminishing returns beyond ~8 wk | pending re-run | Discussion §4.1 (b) |
| Conclusion: weekly re-optimization over 4–8 wk is a "sweet spot" | pending re-run | Discussion §4.1 (c) |
| Conclusion: horizon length mainly drives computing effort | pending re-run | Discussion §4.1 (d) |
| Conclusion: under daily re-optimization all horizons give near-identical solutions | pending re-run | — |
| Conclusion: NI slightly lower continuity (slope heterogeneity) | pending re-run | Speculative cause; keep only if the data support it |
| Conclusion: MIP continuity falls with θ, SA continuity rises | pending re-run | — |
| §4.4.3 Practical implications (Beaudoin; Myers; de Pellegrin Llorente; site-specificity) | rewritten (pending) | Discussion §4.4, only where the new results support it |
| §4.4.4 Limitations: deterministic, semi-synthetic, hardware dependence | kept + extended | Discussion §4.5: adds solver/time-limit dependence, earliness deferral, no WIP value, tiny-production replay rows, no mobilisation costs, single SA seed |
| §4.5 Conclusions | pending re-run | — |
| Figure: runtime vs horizon | pending re-run | Regenerate from re-run summary |
| Figure: continuity vs objective deviation | dropped/rewritten | Replace with continuity vs relative delivered volume |
| Thesis claim "repeated runs identical (MIP) / minimal variation (SA)" | pending | Time-limited MIP is load-dependent. Only true with a deterministic work limit. |
| §4.2.1 "per-solve time limit 1800 s" (no rationale) | kept, now justified | Calibration paragraph in Methods §2.2; Table S1 |
| §4.2.5 Continuity definition (block–machine assignments unchanged between consecutive days) | rewritten | Computed on playback records with volume; descriptive only because moves are free (Methods §2.5) |
