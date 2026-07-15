# Reproduction and Submission Audit Test Report

Date: 2026-07-15

## Test scope

The local source tree and an independently cloned public feature branch were
tested:

- WIP branch: `devin/1784079630-national-power-provenance-audit`
- Public test branch:
  https://github.com/bougtoir/beyond-gdp-national-power/tree/devin/1784079630-provenance-audit
- Public subtree commit tested: `31747c3c880b56d38d943ac6f4631fe98be47474`

The public repository's default branch remains on the previous synchronized
version until the WIP pull request is merged and the scheduled sync workflow
runs. The feature branch above contains only the public repository files and
was used for the clean-clone test.

## Results

| Check | Result | Evidence |
|---|---|---|
| Python compilation | PASS | `python3 -m py_compile` succeeded for the loader, exporters, reproduction runner, audit scripts, analysis scripts, and manuscript generators |
| Local full reproduction | PASS | `python reproduce.py` exited 0 in 587 seconds |
| Public clone and dependency installation | PASS | A new clone and new in-repository virtual environment were created from the public feature branch; `pip install -r requirements.txt` completed |
| Public-clone full reproduction | PASS | Final setup run exited 0 in 582 seconds; the PR test-mode rerun also exited 0 in 596 seconds |
| Initial public-clone attempt | FAIL, FIXED | The first run completed all generators but the final provenance scan entered `.venv` and found a package-internal forbidden word. `reproduce.py` now excludes virtual-environment, Git, and cache directories; the final full run passed |
| Expected generated files | PASS | DOCX, LaTeX, editable PPTX, four PNG figures, highlights, cover letter, supplementary table, audit outputs, reports, and BibTeX were present |
| Canonical row counts | PASS | Dataset 96; variable metadata 16; field-level source supplement 480; auxiliary-dataset applicability 96 |
| Private-path scan | PASS | No WIP or private collection path remained in repository source or generated text |
| Excluded-encyclopedia scan | PASS | No excluded encyclopedia reference remained in repository source or generated text |
| Numeric-literal audit | PASS | 2,401 inventory rows; 0 statistical-result literals requiring replacement |
| Corrupted-input rejection | PASS | Removing one canonical record caused `verify_outputs()` to fail with `expected 96 rows, found 95`; restoring the exact bytes made verification pass |
| Citation reciprocity | PASS | 13 cited keys and 13 bibliography entries; no missing or orphan references |
| LaTeX labels and references | PASS | No missing labels and no unreferenced figure/table labels |
| Abstract and keywords | PASS | Abstract 241 words; six English keywords |
| DOCX figure/table inclusion | PASS | Four inline figures and four editable tables |
| Figure/table citation order and placement | PASS | Tables 1–4 and Figures 1–4 are first cited sequentially and positioned immediately after the relevant citation paragraph, with captions adjacent to the object |
| Editable figure output | PASS | Four widescreen PPTX slides, one figure per slide; no Japanese or CJK text detected |
| Figure files | PASS | Four separate PNGs, 2,370–3,570 pixels wide, approximately 300 DPI |
| Source URL audit | PASS WITH ACCESS LIMITATIONS | 140 unique URLs: 38 HTTP 200, 1 HTTP 202, 1 HTTP 308, 94 HTTP 403, 2 HTTP 405, 2 HTTP 500, and 2 TLS/network errors |
| Source-fabrication screen | PASS WITH SCOPE LIMITATION | No clearly fabricated bibliographic source was identified in the catalog/metadata/access audit; access failure alone was not treated as fabrication, and this is not a complete expert re-verification of every historical claim |
| PDF compilation | UNAVAILABLE | `pdflatex` is not installed; LaTeX sources were generated, but PDF compilation was not claimed |
| Author-side metadata | BLOCKED | Author name, affiliation, postal/corresponding details, email, date, funding, competing interests, CRediT, submission exclusivity, AI declaration confirmation, and archival DOI require author input |

## PR test-mode evidence

The full public-branch pipeline was run again after PR creation:

```text
Validated canonical row counts, expected outputs, and public-only paths.
TEST1_EXIT=0
TEST1_SECONDS=596
```

The generated-output assertions returned:

```text
records=96; variable_metadata=16; source_rows=480
public_dataset_applicability=96; url_rows=140; numeric_rows=2396
statistical_result_literal blockers=0
DOCX: abstract_words=241, inline_shapes=4, tables=4
PPTX: slides=4, slides_with_CJK_text=0
citations=13, bibliography_entries=13, figure/table_labels=8
pipeline_scripts=13
TEST2_EXIT=0
```

The deliberate regression probe returned:

```text
RuntimeError: data/polity_period_records.csv: expected 96 rows, found 95
PASS restored input accepted
TEST3_EXIT=0
```

An initial artifact-check assertion used a stale internal LaTeX label name
(`fig:regression`). Inspection showed the generated manuscript consistently
uses `fig:forest-plot`; the test expectation was corrected and the complete
artifact check then passed. No repository code change was required.

## Post-review regression check

Devin Review identified an unmatched LaTeX math delimiter after a generated
percentage. The generator and committed LaTeX were corrected. A static check
confirmed that no percentage is followed by the stray delimiter, every
generated line has an even number of unescaped math delimiters, and environment
and brace counts are balanced. The repository-level `verify_outputs()` check
also passes after the report's excluded-source label was phrased without the
forbidden literal.

The fix was then regenerated from a fresh clone of public feature-branch commit
`4bd343ae3ab6e0c3b4b96e63e202450c5bfc4c30`. The generator exited 0, the exact
output `86.4\%, Fisher $p = 0.0204$.` was present, and the broken `\%$,` token
was absent from the source and every generated LaTeX file. An adversarial
in-memory probe reintroduced the old token and the delimiter checker rejected
it at manuscript line 137; the corrected file and `verify_outputs()` both
passed. Direct PDF compilation remains untested because `pdflatex` is not
installed.

## Post-review resilience checks

Two additional review findings were reproduced and fixed:

- A synthetic non-converged multivariate model now generates explanatory
  Fig. 4 output plus PPTX, DOCX, and LaTeX fallbacks without dereferencing an
  empty coefficient dictionary. The regression table is omitted, the DOCX
  contains three sequentially numbered tables, the PPTX retains four cited
  figure slides, and no conditional coefficient claim is emitted.
- An empty source catalog now produces a header-only URL-status CSV with zero
  rows instead of indexing an empty result list.

Both targeted probes passed. Normal-data DOCX and LaTeX regeneration,
Python compilation, `git diff --check`, the 2,401-row numeric inventory with
zero statistical-result blockers, and `reproduce.verify_outputs()` also pass.

## Reproduction determinism

The clean public run left the tracked LaTeX, BibTeX, JSON report, CSV inputs
other than the line-number inventory, and PNG figures byte-identical to the
published branch. DOCX and PPTX packages regenerated with the same document
structure, dimensions, counts, and text but different internal package
metadata, so byte-for-byte Office archive identity is not claimed.

## Scientific interpretation

Computational reproducibility passes. Measurement validity does not thereby
pass:

- eight principal fields remain AI-assisted subjective legacy codings;
- the 96 cases are not a probability sample;
- original coding had no prespecified rubric, outcome blinding, independent
  raters, or agreement assessment;
- several closure, outcome, and patron classifications remain contradicted,
  contested, or not independently verified;
- the technical-exclusion reclassification is post hoc; and
- the analyses do not establish causal identification.

The repository is therefore suitable as a transparent AI-assisted exploratory
dataset and sensitivity analysis, not as a validated public-data measurement
dataset or confirmatory causal study.
