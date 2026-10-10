# CJFR submission checklist (Research article)

Source: `notes/cjfr-guidelines.md`. Status: ✅ done · ⏳ pending results · ❗ needs author input.

| # | Requirement | Status | Where / note |
|---|---|---|---|
| 1 | Research article: ≤ 6000 words Introduction→Discussion, ≤ 50 references | ⏳ | `python scripts/wordcount.py` (2026-10-10: 3386 words + placeholders; target in `notes/open-questions.md`) |
| 2 | Abstract ≤ 200 words, one paragraph, no citations | ⏳ | 142 words + findings placeholders |
| 3 | Keywords after abstract | ✅ | `sections/abstract.tex` |
| 4 | Double-spaced, single column, page numbers, continuous line numbers, Letter | ✅ | `main.tex` (setspace, lineno) |
| 5 | Order: title page, abstract, keywords, body, acknowledgements, references | ✅ | `main.tex` |
| 6 | Title page: names, affiliations (dept, institution, city, province, country), corresponding e-mail | ✅ | `metadata.tex` (same as the SoftwareX manuscript) |
| 7 | Competing interests statement (title page and submission form) | ✅ | `metadata.tex`: G.P. leads FHOPS development (non-financial); none other. Repeat in ScholarOne |
| 8 | Funding statement (agency in full, grant numbers) | ✅ | `metadata.tex` (NSERC RGPIN-2023-04197, FRESH, BRIMM) |
| 9 | Author contributions (CRediT, initials) | ✅ | `sections/statements.tex` (agreed 2026-10-10; formal analysis G.P. only). Enter in ScholarOne with levels: lead = first-named in `notes/open-questions.md` |
| 10 | Data availability statement (repository, DOI, link) | ❗ | text done. Make both repos public, cut GitHub releases (Zenodo integration), insert DOIs |
| 11 | Generative AI disclosure (tool name and version; writing help in Acknowledgements, research use in Methods) | ✅/❗ | Acknowledgements and Methods, generic wording per G.P. policy (no vendor or model names; CSP asks for names and versions, and G.P. accepts that deviation). Before submission G.P. must do the code review the Methods sentence claims (spot-check `analyze_rerun.py` against run JSONs). Repeat the disclosure in ScholarOne |
| 12 | Harvard references, alphabetical, DOIs where possible | ✅/❗ | `cjfr-apalike-doi.bst`; 19 DOIs added. Thesis URL resolved. Still to resolve: FHOPS archive DOI, Zenodo version check |
| 13 | Submitted work not in the reference list | ✅ | SoftwareX paper cited in text only (`\fhopspaper`); systematic review removed |
| 14 | Equations numbered flush left | ✅ | `amsmath` `leqno` (no displayed equations yet) |
| 15 | Figures/tables cited in order, self-contained captions | ⏳ | Fig. 1 and Table 1 done; Figs. 2–3 and Tables 2–3 generated after the grid |
| 16 | Figures ≥ 300 dpi / vector PDF | ✅ | all figures are vector PDF |
| 17 | Tables editable at production | ⏳ | LaTeX tables; provide DOCX/XLSX if requested after acceptance |
| 18 | Supplementary material numbered S1…, cited by footnote | ✅/⏳ | `supplement.tex` (Tables S1–S2; S3 per-run table pending) |
| 19 | LaTeX for ScholarOne: figures without `./`, all files in one folder, inline `.bbl` if needed | ⏳ | flatten at packaging (Phase 5) |
| 20 | Cover letter | ⏳ | `submission/cover-letter.tex` (findings, referees pending) |
| 21 | Suggested referees (optional, no collaborators) | ❗ | authors |
| 22 | All authors approve submission, incl. conclusions differing from Ch. 4 | ❗ | sign-off memo after the analysis |
| 23 | No `\pending{}` left | ⏳ | `grep -rn pending manuscript/sections manuscript/metadata.tex` |
