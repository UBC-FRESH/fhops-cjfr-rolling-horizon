# ADR 0001: Quality gates for the manuscript repository

Status: proposed on 2026-10-16. Pending the maintainer's decision.
Date: 2026-10-16
Issues: P0.2 (to be created with the phase)
Related: ADR 0006 and the quality-gates page of the UBC-FRESH dev workflow

## Context

This repository holds a LaTeX manuscript, the analysis scripts that generate its tables,
figures and numbers, and the committed results those scripts read. It was built before the
UBC-FRESH dev workflow, so it has no validator, dashboard, lint, type, or test configuration.
A paper whose numbers are generated can drift from its results without any gate noticing.

## Options

- **A. Seed gates only.** Lint, format, strict types, tests with the 95 percent branch-coverage
  gate, validator, and the docs build. The LaTeX paper is not gated.
- **B. Seed gates, plus two project gates.** `manuscript`: the paper, cover letter and supplement
  build with tectonic, with no undefined references or citations. `assets`: the scripts regenerate
  every table, figure and number from `results/`, and `git diff --exit-code` shows no change.
- **C. Option B, with the docs gate removed.** The repository has no Sphinx site, so the docs gate
  would be a stub.

## Recommendation

Option B. The docs gate stays in its seed form and checks a minimal Sphinx site with the paper's
method notes (see P0.2). Option C would remove a seed gate, which needs an ADR and the maintainer's
decision. Option B adds gates and removes none.

## Consequences

- Each gate has a command, and the dashboard runs them all.
- The `assets` gate depends on the analysis being deterministic (P0.5). Until P0.5 lands, the gate
  is red by design, and no merge happens.
- CI runs the dashboard on pull requests, as in the seed. Branch protection is an approved settings
  change, not part of this ADR.
