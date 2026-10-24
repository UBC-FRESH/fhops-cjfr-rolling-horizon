# CJFR submission checklist (Research article)

Source: `notes/cjfr-guidelines.md`. Status: ✅ done · ⏳ pending results · ❗ needs author input.

| # | Requirement | Status | Where / note |
|---|---|---|---|
| 1 | Research article: ≤ 6000 words Introduction→Discussion, ≤ 50 references | ✅ | `python scripts/wordcount.py` (2026-10-18: body 4800/6000; abstract 200/200; 42 references) |
| 2 | Abstract ≤ 200 words, one paragraph, no citations | ✅ | 200 words |
| 3 | Keywords after abstract | ✅ | `sections/abstract.tex` |
| 4 | Double-spaced, single column, page numbers, continuous line numbers, Letter | ✅ | `main.tex` (setspace, lineno) |
| 5 | Order: title page, abstract, keywords, body, acknowledgements, references | ✅ | `main.tex` |
| 6 | Title page: names, affiliations (dept, institution, city, province, country), corresponding e-mail | ✅ | `metadata.tex` (same as the SoftwareX manuscript) |
| 7 | Competing interests statement (title page and submission form) | ✅ | `metadata.tex`: G.P. leads FHOPS development (non-financial); none other. Repeat in ScholarOne |
| 8 | Funding statement (agency in full, grant numbers) | ✅ | `metadata.tex` (NSERC RGPIN-2023-04197, FRESH, BRIMM) |
| 9 | Author contributions (CRediT, initials) | ✅ | `sections/statements.tex` (agreed 2026-10-10; formal analysis G.P. only). Enter in ScholarOne with levels: lead = first-named in `notes/open-questions.md` |
| 10 | Data availability statement (repository, DOI, link) | ✅ | Zenodo dataset DOI **10.5281/zenodo.23626401** (`v1.1.1-rerun-m7`, minted automatically from the GitHub release), cited as `jaffray2026rerun`; analysis code archived as **10.5281/zenodo.23626443** (`jaffray2026analysis`) |
| 11 | Generative AI disclosure (tool name and version; writing help in Acknowledgements, research use in Methods) | ✅ | Acknowledgements and Methods name Claude Opus 5.5 (Anthropic, via OpenCode), per the CSP wording. Methods also discloses Kimi K3 (original rolling-horizon runner) and OpenAI GPT-5.x (several versions; FHOPS design, implementation and testing). The code check behind the Methods sentence is recorded in `results/rerun/CODE_REVIEW.md` (234 runs, 936 field comparisons). Repeat the disclosure in ScholarOne |
| 12 | Harvard references, alphabetical, DOIs where possible | ✅ | `cjfr-apalike-doi.bst`; DOIs added, including the systematic review (10.1080/14942119.2026.2662184), FHOPS 1.0.1 (10.5281/zenodo.23244315), the SoftwareX paper (10.1016/j.softx.2026.103147), the dataset (10.5281/zenodo.23626401) and the analysis archive (10.5281/zenodo.23626443). Scenario record 10.5281/zenodo.19200385 confirmed to contain the scenario bundles (93 files under `data/input/scenarios/`) |
| 13 | Submitted work not in the reference list | ✅ | This manuscript is not in the list. The FHOPS SoftwareX paper is now **published** (SoftwareX 36, 103147, doi:10.1016/j.softx.2026.103147) and is a normal reference entry (`paradis2026fhops`) |
| 14 | Equations numbered flush left | ✅ | `amsmath` `leqno` (no displayed equations yet) |
| 15 | Figures/tables cited in order, self-contained captions | ✅ | Figs. 1–3, Tables 1–4 (Table 4 = Ch. 4 re-test) |
| 16 | Figures ≥ 300 dpi / vector PDF | ✅ | all figures are vector PDF |
| 17 | Tables editable at production | ⏳ | LaTeX tables; provide DOCX/XLSX if requested after acceptance |
| 18 | Supplementary material numbered S1…, cited by footnote | ✅ | `supplement.tex` (Tables S1–S2 rendered; S3 described and deposited as the machine-readable per-run CSV) |
| 19 | LaTeX for ScholarOne: figures without `./`, all files in one folder, inline `.bbl` if needed | ✅ | `scripts/package_submission.py` → `submission/package/` |
| 20 | Cover letter | ✅ | `submission/cover-letter.tex` (findings, competing interests, suggested referees and the referee COI disclosure filled); package rebuilt 2026-10-24 with the cover-letter PDF |
| 21 | Suggested referees (optional, no collaborators) | ✅ | `submission/cover-letter.tex`: Rönnqvist (Laval), Chung (Oregon State), McDill (Penn State), Ouhimmou (ÉTS), with a COI disclosure. Draft pool and relationship notes in `notes/referee-candidates.md`; enter in ScholarOne |
| 22 | All authors approve submission, incl. conclusions differing from Ch. 4 | ✅ | Self-sign-off by G.P. on behalf of all authors (2026-10-24, per instruction); the conclusions differing from Ch. 4 are stated in the Discussion |
| 23 | No `\pending{}` left | ✅ | manuscript and cover letter render with no `Pending:` marker (checked in the extracted PDF text, 2026-10-20). The `metadata.tex` fallbacks are overridden by `generated/numbers.tex` |
