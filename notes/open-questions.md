# Open questions and decisions

## Decided
- 2026-10-10: CRediT roles (G.P.). G.P. acquired both the NSERC and the BRIMM funding. For the
  ScholarOne levels, the first-named author in each row is lead and the others are supporting.

  | Role | Authors |
  |---|---|
  | Conceptualization | R.J., G.P. |
  | Data curation | R.J. (scenarios), G.P. (re-run outputs) |
  | Formal analysis | G.P. (+R.J. if she interprets the re-run results at sign-off) |
  | Funding acquisition | G.P. |
  | Investigation | R.J. (original experiments), G.P. (re-run, calibration) |
  | Methodology | R.J., G.P. |
  | Project administration | G.P. |
  | Resources | G.P. |
  | Software | G.P. |
  | Supervision | K.C., G.P. |
  | Validation | G.P. |
  | Visualization | G.P. |
  | Writing – original draft | R.J. (thesis Ch. 4), G.P. (this manuscript) |
  | Writing – review & editing | R.J., K.C., G.P. |
- 2026-10-10: Competing interests disclose that G.P. leads FHOPS development (non-financial).
- 2026-10-10: Title page uses the SoftwareX affiliation for all authors (Faculty of Forestry &
  Environmental Stewardship, UBC, 2424 Main Mall, Vancouver, BC V6T 1Z4). Corresponding author
  G. Paradis, gregory.paradis@ubc.ca, +1 604 822 1890.
- 2026-10-10: Funding statement from the SoftwareX acknowledgements: NSERC Discovery Grant
  RGPIN-2023-04197 (G.P.; part of R.J.'s stipend), FRESH lab funds (G.P.), BRIMM (K.C.'s salary).
- 2026-10-10: Thesis citation: UBC Open Collections item 1.0452424
  (https://open.library.ubc.ca/collections/ubctheses/24/items/1.0452424).
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
- AI-use disclosure wording (draft in Acknowledgements).
- Suggested referees (optional).
- Data deposit (decided 2026-10-10, G.P.): open GitHub repos in UBC-FRESH. A versioned GitHub
  release triggers a Zenodo archive and DOI. Still to do: make both repos public, cut the releases
  and insert the DOIs.
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

## Length budget (CJFR research article: 6000 words Introduction→Discussion)
G.P. (2026-10-10): a 2500-word body is too short. The gap was unwritten results and discussion
plus an over-tightened introduction, not a lack of content. Target:

| Section | Target | Now (2026-10-10) |
|---|---|---|
| Introduction | 1000–1200 | 966 |
| Materials and methods | 1500–1700 | 1461 |
| Results | 1400–1700 | placeholders |
| Discussion + Conclusions | 1600–1900 | 933 (results-independent parts) |
| Total | ≤ 6000 | 3386 |
