# Open questions and decisions

## Decided
- 2026-10-09: CJFR **Research article**; authors Jaffray, Coupland, Paradis (corresponding: Paradis);
  all authors sign off before submission, including conclusions that differ from Ch. 4.
- 2026-10-10: **MIP arm** uses Gurobi 13.0.3, cold start, 1 thread, 1800 s stage 1 and 900 s
  earliness per window; 36 MIP + 34 SA workers (option B). Evidence in jaffray-masc-fhops-model
  `notes/rolling_rerun_v101.md`.
- 2026-10-10 (proposed in the analysis script; confirm with results): report relative delivered
  volume against **both** references (same-method full-horizon baseline and best known plan).
  Figures use the best known plan.
- 2026-10-10 (proposed): material sequencing violations = violations from a replay with a
  1e-3 m³ volume tolerance (FHOPS default 1e-6). Both counts are reported.
- Machine moves and continuity are computed from playback records that produced volume. Moves
  are free in these scenarios, so both metrics are descriptive only (stated in Methods and
  Limitations).

## Needs author input (before submission)
- Corresponding e-mail and departments (title page).
- Funding agencies and grant numbers.
- CRediT roles (draft in `sections/statements.tex`).
- Competing-interest wording (G.P. leads FHOPS development).
- AI-use disclosure wording (draft in Acknowledgements).
- Suggested referees (optional).
- Thesis citation: cIRcle handle/DOI.
- Data deposit: Dryad (free through 2026 via the submission e-mail) or Zenodo. Make both GitHub
  repos public at submission.
- FHOPS 1.0.1 archive DOI (Zenodo release), if one is wanted for the software citation.
- Confirm that Zenodo record 19200385 matches the scenario bundles used (`data/input/scenarios/`
  in the experiment repo, generated 2026-02-28).

## Open analysis questions (after the grid)
- Whether RQ "do different horizons converge to similar solutions?" (thesis RQ3) should come back
  with a plan-similarity metric, or stay folded into RQ1.
- Whether to add a supplementary per-run table (Table S3) or point to the data deposit only.
- How to present the effect of the earliness limit on long windows, if it shows in the grid.

## FHOPS issues raised from this work
- UBC-FRESH/fhops#157 (comment): tiny-production rows also occur in stage 1 with Gurobi.
- Candidate for 1.0.2: per-stage solver options (deterministic `WorkLimit` per stage). Not filed
  yet; file if the paper needs it.
