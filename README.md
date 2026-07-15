# Beyond GDP National Power

Exploratory historical analysis of resource-base orientation, network closure,
and polity outcomes across 96 polity-period cases.

## Data status

This repository is computationally reproducible, but the current dataset is not
an observational public-data extract.

- The author supplied the research question and concepts, but no record-level
  numerical values.
- Devin AI created 54 records on 13 May 2026 and later added 42 records, for a
  total of 96.
- `dominant`, `stock_index`, `trade_openness`, `geo_barrier`,
  `external_threat`, `relative_pop`, `tech_position`, and
  `institutional_quality` are legacy values in an AI-assisted exploratory
  dataset. They were not calculated from public datasets and were not
  independently rated.
- `closure_type`, `outcome`, and `has_external_patron` are historically
  anchored classifications, but the original dataset did not include
  record-level sources or a prespecified coding rubric.
- The 0–1 scores must not be described as observed measurements or validated
  expert ratings. Readers may edit them in
  `data/polity_period_records.csv` and rerun the pipeline.

The audit tables document field provenance, record lineage, numeric literal
use, and relevant Devin sessions. `audit/supplementary_case_sources.csv`
contains 480 field-level rows covering `entity`, `period`, `closure_type`,
`outcome`, and `has_external_patron` for all 96 records. Its status column
distinguishes supported, contested, contradicted, and not independently
verified legacy values.

## Reproduce the analyses

Python 3.10 or later is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python reproduce.py
```

The full analysis and manuscript build take several minutes because the
mediation, simulation, and sensitivity scripts use fixed-seed bootstrap or
Monte Carlo procedures. DOCX, PPTX, LaTeX, reports, and figures are regenerated.
PDF compilation additionally requires a local LaTeX installation; the LaTeX
source is still generated when a compiler is unavailable. The bundled
Springer Nature class is retained only as a reproducible renderer and is not a
claim of journal-template compliance.

## Main files

- `data.py`: canonical CSV loader plus field-level provenance declarations
- `data/polity_period_records.csv`: canonical editable dataset of 96 records
- `data/variable_metadata.csv`: field origin and measurement-status labels
- `audit/case_source_catalog.csv`: reviewed case-level source catalog
- `audit/supplementary_case_sources.csv`: 96 cases × 5 sourced fields
- `audit/public_dataset_applicability.csv`: temporal applicability of Seshat
  Cliopatria, Maddison, Clio-Infra, HYDE, V-Dem, COW, and Polity
- `audit/PROVENANCE_AUDIT.md`: record-construction and measurement provenance
- `audit/NUMERIC_LITERAL_AUDIT.md`: classified inventory of numeric literals
- `audit/SOURCE_URL_AUDIT.md`: URL-access and source-fabrication checks
- `audit/audit_source_urls.py`: optional repeatable URL-access probe
- `audit/source_url_status.csv`: latest URL-access probe results
- `audit/REVIEWER_PERSPECTIVE_AUDIT.md`: prioritized scientific review
- `audit/EEH_SUBMISSION_COMPLIANCE.md`: journal-guideline checklist
- `analysis.py`: descriptive and logistic-regression analyses
- `mediation.py`, `serial_mediation.py`: mediation analyses
- `modern_analysis.py`: explicitly labeled modern-state scenarios
- `sensitivity_technical_network_exclusion.py`: exclusion reclassification
- `causal_analysis.py`: IV, propensity-score, and robustness diagnostics
  (not a claim of causal identification)
- `reports/`: generated text and JSON outputs
- `figures/`: generated sensitivity figures
- `manuscript/`: generated DOCX/LaTeX manuscript, editable supplementary
  table, cover letter, submission highlights, editable figure PPTX, and
  separate figure files

## Interpretation

Rerunning the code establishes that the same inputs and fixed analysis settings
produce the same reported statistical results. It does not validate the subjective codings, the
sample-selection process, causal identification, or historical classifications.
These outputs should be treated as exploratory until contested factual fields
are adjudicated under an explicit rule and the subjective fields are
independently recoded under a prespecified rubric.
