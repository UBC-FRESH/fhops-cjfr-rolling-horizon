# Roadmap

## Phase 0 — Orientation and repository
- [x] Read thesis Ch. 4, re-run notes, FHOPS 1.0.1 release notes (known limitations).
- [x] CJFR author guidelines summarised (`notes/cjfr-guidelines.md`).
- [x] Decisions (2026-10-09, G. Paradis): repo `UBC-FRESH/fhops-cjfr-rolling-horizon` (private);
      authors Jaffray, Coupland, Paradis (corr. Paradis); all authors sign off before submission;
      article type **Research article**.
- [x] Repository created; contract, changelog, roadmap.

## Phase 1 — Re-run feasibility (in `jaffray-masc-fhops-model`)
- [x] `fhops==1.0.1` venv; harness `--smoke` (10/10 ok).
- [x] Probe: size-18/40 MIP windows at 1800 s on HiGHS and Gurobi (time, peak memory).
- [x] Time-limit calibration (Gurobi, 7200 s + 1800 s, incumbent/bound trajectories).
- [x] Decided (2026-10-10, option B): Gurobi, 1800 s + 900 s earliness, 36 MIP + 34 SA workers.
- [x] Wall-clock estimate and launch command → go given 2026-10-10.

## Phase 2 — Grid run
- [x] Launched 2026-10-10 17:27 UTC (`data/output/rerun_v101_gurobi/`, worst case about 4.5 days).
- [ ] Grid complete; `--summarize`.

## Phase 3 — Manuscript skeleton (while the grid runs)
- [x] CJFR LaTeX skeleton (title page, abstract, keywords, Introduction, Materials and methods,
      Results/Discussion placeholders, limitations, statements, references); builds to PDF.
- [x] `notes/ch4-to-cjfr-map.md`.

## Phase 4 — Analysis
- [ ] Scripts: stitched-plan metrics vs full-horizon baselines; figures/tables from `summary.csv`.
- [ ] Ch. 4 conclusions confirmed or revised, explicitly.
- [ ] Results and Discussion written; author sign-off memo.

## Phase 5 — Submission package
- [ ] PDF, source, figures, cover letter draft, CJFR checklist; hand-off for upload.
