# FHOPS rolling-horizon machine scheduling — CJFR manuscript

Manuscript for a *Canadian Journal of Forest Research* research article derived from Chapter 4 of
R. Jaffray's MASc thesis (*Development and Evaluation of an Open-Source Tool for Machine Scheduling
in Forest Operational Planning*, UBC, 2026). The experiment is re-run on FHOPS 1.0.1, which carries
state between rolling-horizon windows, and every run is scored on its stitched plan.

Authors: Rosalia Jaffray, Kathleen Coupland, Gregory Paradis (corresponding).

- Experiment code and results: `UBC-FRESH/jaffray-masc-fhops-model` (branch
  `feature/rolling-rerun-v101`, issue #1).
- FHOPS: <https://github.com/UBC-FRESH/fhops> (tag `v1.0.1`, PyPI `fhops==1.0.1`).

## Build
```
cd manuscript && tectonic --keep-intermediates -o build main.tex   # keeps main.bbl for packaging
```

See `AGENTS.md` for the working contract and `ROADMAP.md` for status.
