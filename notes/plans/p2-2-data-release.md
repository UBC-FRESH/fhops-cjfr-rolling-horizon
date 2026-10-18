# P2.2 data release plan (queued for approval)

Phase: P2 (#37). Branch: `feature/p2-submission`.

Goal: make the data public, archived, and citable, and insert the DOIs into the manuscript. Per
ADR 0008 every visibility change, tag, release, and DOI is named here and runs only after its own
approval.

## Current state (2026-10-18)

- `UBC-FRESH/jaffray-masc-fhops-model` (scenarios, runner, run outputs): **public**, with a
  `v1.0.0` release from March 2026 ("Final thesis results"). The FHOPS 1.0.1 re-run outputs
  (`data/output/rerun_v101_gurobi/`) are **not** in any release.
- `UBC-FRESH/fhops-cjfr-rolling-horizon` (this repo, the analysis): made **public** on 2026-10-18
  (G.P. instruction); the data-availability statement cites it as a public URL.
- FHOPS: `v1.0.1` is released on GitHub (2026-10-08); no archive DOI minted.
- `references.bib`: `jaffray2026zenodo` carries a Zenodo DOI (10.5281/zenodo.19200385) flagged
  "confirm version"; `fhops2026v101` is flagged "PENDING: archive DOI".

## Recommended actions (each approved on its own)

1. **Confirm the scenario record.** Check whether the FHOPS 1.0.1 scenario bundles match
   `10.5281/zenodo.19200385`; if not, mint a new version of that Zenodo record and update
   `jaffray2026zenodo`. (Zenodo account: G.P.)
2. **Cut a release for the re-run.** Tag and release `UBC-FRESH/jaffray-masc-fhops-model` (e.g.
   `v1.1.0-rerun`) containing the runner, scenarios, `data/output/rerun_v101_gurobi/` outputs, and
   `summary.csv`, with the release notes stating the FHOPS 1.0.1 provenance.
   ```bash
   gh release create v1.1.0-rerun -R UBC-FRESH/jaffray-masc-fhops-model --title "FHOPS 1.0.1 rolling-horizon re-run" --notes-file <notes>
   ```
3. ~~**Make this repository public**~~ — **done 2026-10-18**:
   `gh repo edit UBC-FRESH/fhops-cjfr-rolling-horizon --visibility public`.
4. **Connect both repositories to Zenodo** and mint a DOI per release (Zenodo's GitHub integration
   mints one DOI per GitHub release once the repo is switched on). Record the concept DOI and the
   version DOI.
5. **Mint the FHOPS 1.0.1 archive DOI** through the same integration on `UBC-FRESH/fhops`
   (the `v1.0.1` release) and update `fhops2026v101` ("PENDING: archive DOI").
6. **Insert the DOIs**: replace the `\pending{...}` in `manuscript/sections/statements.tex` with the
   two version DOIs, and drop the two "PENDING" notes in `references.bib`.
7. **Tag this repository** with the submission release after the DOIs are in, so the archived
   analysis matches the submitted PDFs.

## Not needed (recorded for completeness)

- Gurobi and the case-study scenarios already have their citations; no other external account is
  touched.

## After the release

- P2.3 close-out: rebuild `submission/package/`, re-run the dashboard, and hand off to G. Paradis.
- The author sign-off (#22) and the optional referees (#21) remain author actions.

## Staged on 2026-10-18 (pending one decision and the final grid)

- `.zenodo.json` added to this repository (analysis) for the Zenodo deposition.
- Release-notes draft at `notes/plans/p2-2-experiment-release-notes.md` for the experiment repo.
- **Sequencing:** the outputs of `jaffray-masc-fhops-model` are currently **untracked** (only
  `environment.txt` is committed), so the data-availability statement's "openly available in the
  GitHub repository" is not yet true. The output publication + release + DOI should run **after
  P1.1 completes the grid** (2 SA runs outstanding), so we release the complete grid once rather than
  twice.
- **Open decision (blocks the release):** `jaffray-masc-fhops-model` `notes/repo_cleanup.md` asks
  whether to archive **all** outputs (45 MB, 817 files: per-run JSON, stitched assignment tables, and
  ~5 MB Gurobi logs) or a **representative subset** (per-run JSON + `summary.csv` + manifests, no
  solver logs). Recommendation: commit the JSON, `summary.csv`, assignment tables, and manifests
  (~1-2 MB) to the repository, and attach the full output tree (with logs) as a release asset /
  Zenodo deposit, keeping the git history light.
