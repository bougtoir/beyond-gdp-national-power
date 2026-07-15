# Explorations in Economic History Submission Compliance

Checked: 2026-07-15

Official guide:
https://www.sciencedirect.com/journal/explorations-in-economic-history/publish/guide-for-authors

## Current compliance

| Requirement | Status | Repository implementation |
|---|---|---|
| Editable manuscript source | Pass | DOCX and LaTeX sources are generated |
| Word manuscript single-column | Pass | Generated DOCX uses a single-column layout |
| Abstract no more than 250 words | Pass | Generated abstract is below 250 words |
| One to seven English keywords | Pass | Six English keywords |
| Three to five highlights, no more than 85 characters each | Pass | `manuscript/highlights.docx` contains five checked bullets |
| Editable tables and in-text citations | Pass | Tables are editable and cited in sequence |
| Figures cited and separately supplied | Pass | Four cited PNG figures plus editable PPTX |
| Supplementary files cited and captioned | Pass | Supplementary Table S1 is cited and editable |
| Research data deposited and linked | Partial | Public GitHub link is present; archival DOI is not yet supplied |
| Data availability statement | Pass | Included before references |
| Consistent references and reciprocal citation | Pass | 13 cited keys, 13 bibliography entries, no missing or orphan references |
| Journal reference style | Pass | EEH specifies author-year citations and an alphabetical reference list |
| Generative-AI declaration before references | Pass | Required declaration is generated in DOCX and LaTeX |
| CRediT contribution statement | Blocked on author | Placeholder remains |
| Funding statement | Blocked on author | Placeholder remains |
| Competing-interest statement | Blocked on author | Confirmation placeholder remains |
| Title-page author, affiliation, postal address, and correspondence details | Blocked on author | Placeholders remain |
| Cover-letter date and author contact details | Blocked on author | Placeholders remain |
| Separate figure resolution requirements | Pass | Four PNGs are 2,370–3,570 px wide at approximately 300 DPI |
| Submission exclusivity confirmation | Blocked on author | Cover letter retains an explicit confirmation prompt |

## Reference-style decision

The organization preference for Vancouver numbering does not apply here
because the journal's official guide explicitly requires author-year in-text
citations and an alphabetical reference list. The manuscript therefore retains
author-year style for EEH.

## Journal-specific observations

- EEH accepts Research Articles, Shorter Articles, Surveys and Speculations,
  and Methods Articles.
- Shorter Articles are typically 10–14 manuscript pages plus two or three
  tables and figures.
- Figures must be uploaded separately even when text graphics are also
  positioned in the manuscript.
- Option C research-data instructions require repository deposit and citation
  or an explanation for non-sharing.
- The bundled Springer Nature class is only a local rendering dependency and
  is not an EEH template.

## Submission blockers

1. Replace author, affiliation, postal address, email, corresponding-author,
   and cover-letter date placeholders.
2. Complete the funding, competing-interest, and CRediT statements and confirm
   the AI-use declaration.
3. Preferably archive the exact release in Zenodo or another durable
   repository and replace or supplement the mutable GitHub URL with a DOI.
4. Confirm that the manuscript is not published or under consideration elsewhere.
5. Resolve the scientific issues in `REVIEWER_PERSPECTIVE_AUDIT.md`; mechanical
   format compliance alone does not make the manuscript submission-ready.
