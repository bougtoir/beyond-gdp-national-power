# Provenance and Reproducibility Audit

## Scope

This audit distinguishes computational reproducibility from measurement
validity. It covers the public repository, the private `wip` history, relevant
Devin sessions, the 96-record dataset, generated reports and figures, and the
manuscript generators.

The 96 rows are not 96 countries. They are selected polity-period cases,
including states, dynasties, empires, alliances, economic blocs, and repeated
periods of the same polity.

## Dataset construction reconstructed from logs

The user supplied the conceptual question—what characterizes polities capable
of functioning under maritime or network closure—and requested analyses. No
record-level numerical values from the user were found.

| UTC time | Evidence | Event |
|---|---|---|
| 2026-05-13 09:39:37 | `event-f3a2ceda1e234844aa865a901babc336` | Devin created `data.py` in one edit with 54 records |
| 2026-05-13 09:39:40 | `event-b4fd5ac1279d49d18b0542943cc444e6` | Devin ran `python data.py`; N=54 |
| 2026-05-13 09:59:32 | `event-193923a1c08944cc87cd24d5ce128145` | Devin planned about 40 additions to reach N≈94 |
| 2026-05-13 09:59:33 | `event-0f7bccd81dcf47c0934e416648beab10` | Devin added 42 records in one edit |
| 2026-05-13 09:59:38 | session log | N=96 |
| 2026-05-13 09:59:42 | session log | Devin noted N=96 exceeded the target |

The initial session
`b8007b0c27d44f7a961387806de03a3a` contains no browser or external-search
events before either dataset edit. The later technical-exclusion session
`7561c13286574d1f9bf2c45150dda3ce` contains local repository searches but no
documented external-source retrieval before the classifications were made.

This establishes that the original values were Devin-generated codings, not
values transcribed from a documented public dataset and not values supplied by
the user.

## Field provenance

### Historical or descriptive fields requiring record-level sources

- `entity`
- `period`
- `era`
- `region`
- `regime_duration_yrs`

`regime_duration_yrs` is mechanically consistent with the date range in 76 of
79 automatically parseable records and differs by only one year in the
remaining three because of BC/AD boundary conventions. This supports date
subtraction as its immediate derivation, but the underlying dates still need
record-level historical sources.

### AI-assisted exploratory subjective fields

- `dominant`
- `stock_index`
- `trade_openness`
- `geo_barrier`
- `external_threat`
- `relative_pop`
- `tech_position`
- `institutional_quality`

These values are not public-data measurements or independently validated
expert ratings. All 96 values for six of the seven continuous scores fall on a
0.05 grid. `relative_pop` has 86 of 96 values on that grid. The values may be
retained for an explicitly exploratory, replaceable coding exercise, but must
not be described as observed empirical data.

### Historically anchored classifications requiring sources and rules

- `closure_type`
- `outcome`
- `has_external_patron`

The repository now publishes a 480-row field-level supplement covering all 96
records for `entity`, `period`, `closure_type`, `outcome`, and
`has_external_patron`. Each row contains a source title, author or institution,
URL, locator, excerpt, access time, coding note, verification status, and
applicable auxiliary datasets. A separate 96-row table records temporal
applicability of Seshat, Maddison Project, Clio-Infra, HYDE, V-Dem, Correlates
of War, and Polity5.

The supplement does not convert unsupported legacy codings into verified
facts. In particular, all 60 `closure_type=none` rows and 79
`has_external_patron=0` rows are explicitly marked as not independently
verified rather than claiming that a general historical overview proves the
absence of every possible closure or patron relationship. The source audit also
records nine closure classifications contradicted by their source, four
contested partial restrictions, four classifications varying by subperiod, and
four additional contested or contradicted category assignments.

This is useful for error detection and transparent recoding, but it is not a
substitute for a prespecified rubric or independent coders. Important flagged
cases include:

- `closure_type`: Western Roman Empire, late Byzantine Empire, late Ottoman
  Empire, Inca Empire, Aztec Empire, Ethiopian Empire, Switzerland,
  Yugoslavia, and Korean Empire
- `outcome`: Ethiopian Empire
- `era`: Yuan dynasty
- `has_external_patron`: Ryukyu Kingdom
- `region`: Hawaiian Kingdom

These cases require an explicit classification rule and, where the supplement
currently relies on a broad reference overview, more specific scholarly
support before the revised dataset is treated as validated.

## Sample and outcome lineage

| Revision | N | Outcome counts |
|---|---:|---|
| `f3309fd` | 54 | conquered 32; survived 22 |
| `e268fda` | 96 | conquered 64; survived 32 |
| `4fd95f8` | 96 | overtaken 46; disrupted 18; survived 32 |
| `b9dbb9c` | 96 | overtaken 44; disrupted 20; survived 32 |

No fields in the initial 54 records changed when 42 cases were added. The
54-to-96 edit was additive and explicitly associated with a power/sample-size
target rather than a documented sampling frame.

The three-category conversion changed the `outcome` label for the 64 original
conquered cases. The later borderline branch changed only:

- Hanseatic League: `overtaken` → `disrupted`
- Umayyad Caliphate: `overtaken` → `disrupted`

Current `master` and the public repository contain 46 overtaken, 18 disrupted,
and 32 survived cases; the borderline branch contains 44, 20, and 32.

## Public-repository execution

A clean Python 3.10 virtual environment was created with pinned versions later
recorded in `requirements.txt`. The following public scripts all exited
successfully:

1. `data.py`
2. `analysis.py`
3. `mediation.py`
4. `serial_mediation.py`
5. `modern_analysis.py`
6. `sensitivity_technical_network_exclusion.py`
7. `plot_sensitivity.py`
8. `causal_analysis.py`

The committed sensitivity text report reproduced byte-for-byte. The causal
JSON changed only at floating-point rounding levels around 1e-16. Regenerated
PNG files had identical dimensions and substantively identical content but
were not byte-identical; 0.04%–0.36% of pixels changed, consistent with
rendering differences under an unpinned graphics environment.

Before this audit, the public repository had no README, dependency file, or
one-command runner. The revised package adds pinned dependencies, the canonical
editable CSV, metadata, source supplements, and `reproduce.py`, and updates the
synchronization mapping so the public repository receives the manuscript
generators and generated outputs. Final clean-clone results are reported in
`test-report.md`.

## Hard-coded numeric values

The current static inventory contains 2,448 rows, including canonical CSV
inputs and numbers embedded in prose strings:

| Category | Count |
|---|---:|
| Subjective AI-assisted input values | 672 |
| Historically anchored input values | 192 |
| Simulation or scenario parameters | 219 |
| Candidate definitions or analysis parameters | 80 |
| Analysis thresholds or output labels | 65 |
| Display or layout constants | 248 |
| Dynamically generated values or format precision | 76 |
| Bibliographic, historical, structural, prose, and other code constants | 896 |

Not every literal is problematic. Display constants, fixed random seeds, and
explicitly labeled simulation parameters are legitimate. The main provenance
problem was that the 0–1 dataset scores were presented as coded historical
variables without an explicit AI-subjective origin. They are now published as
editable CSV inputs and labeled as AI-assisted exploratory coding. Statistical
results in manuscript prose are generated from the current analysis; the
current inventory contains zero `statistical_result_literal` release blockers.
The detailed inventory remains intentionally broad so that readers can inspect
and modify thresholds, scenarios, and candidate definitions.

## Conclusion

The code can substantially reproduce the committed analyses from the current
inputs. The repository did not, however, establish that the original
record-level values came from public data or cited historical sources.

The supported wording is:

> The dataset contains Devin-generated exploratory coding literals with no
> original record-level source linkage. The user supplied the concepts but not
> the record values. Computational reproducibility is demonstrated; measurement
> validity and unbiased sample construction are not.

These facts do not by themselves prove intentional fabrication. They do mean
that the dataset must be labeled as AI-assisted exploratory material,
that factual classifications require record-level sourcing, and that empirical
or causal claims should be weakened until independent recoding and validation
are available.
