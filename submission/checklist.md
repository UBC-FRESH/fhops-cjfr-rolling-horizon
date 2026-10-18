# CJFR submission checklist (Research article)

Source: `notes/cjfr-guidelines.md`. Status: ✅ done · ⏳ pending results · ❗ needs author input.

| # | Requirement | Status | Where / note |
|---|---|---|---|
| 1 | Research article: ≤ 6000 words Introduction→Discussion, ≤ 50 references | ✅ | `python scripts/wordcount.py` (2026-10-18: body 4786/6000; abstract 200/200; 42 references) |
| 2 | Abstract ≤ 200 words, one paragraph, no citations | ✅ | 200 words |
| 3 | Keywords after abstract | ✅ | `sections/abstract.tex` |
| 4 | Double-spaced, single column, page numbers, continuous line numbers, Letter | ✅ | `main.tex` (setspace, lineno) |
| 5 | Order: title page, abstract, keywords, body, acknowledgements, references | ✅ | `main.tex` |
| 6 | Title page: names, affiliations (dept, institution, city, province, country), corresponding e-mail | ✅ | `metadata.tex` (same as the SoftwareX manuscript) |
| 7 | Competing interests statement (title page and submission form) | ✅ | `metadata.tex`: G.P. leads FHOPS development (non-financial); none other. Repeat in ScholarOne |
| 8 | Funding statement (agency in full, grant numbers) | ✅ | `metadata.tex` (NSERC RGPIN-2023-04197, FRESH, BRIMM) |
| 9 | Author contributions (CRediT, initials) | ✅ | `sections/statements.tex` (agreed 2026-10-10; formal analysis G.P. only). Enter in ScholarOne with levels: lead = first-named in `notes/open-questions.md` |
| 10 | Data availability statement (repository, DOI, link) | ❗ | text done; steps queued in `notes/plans/p2-2-data-release.md` (make this repo public, cut the re-run release, mint Zenodo DOIs, insert them). Needs G.P. approval and the Zenodo account |
| 11 | Generative AI disclosure (tool name and version; writing help in Acknowledgements, research use in Methods) | ✅/❗ | Acknowledgements and Methods name Claude Opus 5.5 (Anthropic, via OpenCode), per the CSP wording. Methods also discloses Kimi K3 (original rolling-horizon runner) and OpenAI GPT-5.x (several versions; FHOPS design, implementation and testing). Before submission G.P. must do the code review the Methods sentence claims (spot-check `analyze_rerun.py` against run JSONs). Repeat the disclosure in ScholarOne |
| 12 | Harvard references, alphabetical, DOIs where possible | ✅/❗ | `cjfr-apalike-doi.bst`; DOIs added, including the published systematic review (10.1080/14942119.2026.2662184) and the FHOPS 1.0.1 archive (10.5281/zenodo.23244315). Thesis URL resolved. Still to resolve: the scenario Zenodo version check and the two repository-release DOIs (`notes/plans/p2-2-data-release.md`) |
| 13 | Submitted work not in the reference list | ✅ | SoftwareX paper cited in text only (`\fhopspaper`), now **in press** (accepted 2026-10); promote to a reference entry once it has a volume/DOI |
| 14 | Equations numbered flush left | ✅ | `amsmath` `leqno` (no displayed equations yet) |
| 15 | Figures/tables cited in order, self-contained captions | ✅ | Figs. 1–3, Tables 1–4 (Table 4 = Ch. 4 re-test) |
| 16 | Figures ≥ 300 dpi / vector PDF | ✅ | all figures are vector PDF |
| 17 | Tables editable at production | ⏳ | LaTeX tables; provide DOCX/XLSX if requested after acceptance |
| 18 | Supplementary material numbered S1…, cited by footnote | ✅ | `supplement.tex` (Tables S1–S2 rendered; S3 described and deposited as the machine-readable per-run CSV) |
| 19 | LaTeX for ScholarOne: figures without `./`, all files in one folder, inline `.bbl` if needed | ✅ | `scripts/package_submission.py` → `submission/package/` |
| 20 | Cover letter | ✅/❗ | `submission/cover-letter.tex` (findings and competing interests filled; referees pending) |
| 21 | Suggested referees (optional, no collaborators) | ❗ | authors |
| 22 | All authors approve submission, incl. conclusions differing from Ch. 4 | ❗ | sign-off memo after the analysis |
| 23 | No `\pending{}` left | ❗ | only the Zenodo DOI in `statements.tex` (P2 data release). The `metadata.tex` macro fallbacks are all overridden by `generated/numbers.tex`; the supplement's Table S3 placeholder is now the described deposit CSV |
