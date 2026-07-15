# Numeric Literal Audit

This inventory separates canonical input values, subjective AI-assisted scores, analysis/scenario parameters, layout constants, historical/bibliographic numbers, dynamically generated manuscript values, and potentially hard-coded statistical results.

- Inventory rows: 2396
- High-priority rows: 672
- Medium-priority rows: 1172
- Statistical result literals requiring replacement: 0

## Classification counts

| Classification | Rows |
|---|---:|
| `analysis_parameter_or_threshold` | 57 |
| `analysis_threshold_or_output_label` | 8 |
| `audit_implementation_literal` | 7 |
| `bibliographic_or_source_number` | 37 |
| `candidate_definition_or_analysis_parameter` | 80 |
| `code_constant_requires_context` | 460 |
| `display_or_layout_constant` | 251 |
| `dynamically_generated_value_or_format_precision` | 76 |
| `historical_date_or_prose_number` | 38 |
| `historically_anchored_input_value` | 192 |
| `manuscript_structure_or_cross_reference` | 77 |
| `prose_or_label_number` | 213 |
| `sample_size_or_candidate_count_literal` | 9 |
| `simulation_or_scenario_parameter` | 219 |
| `subjective_ai_assisted_input_value` | 672 |

## Interpretation

- Values in `data/polity_period_records.csv` are deliberately published inputs, not hidden code constants. The subjective fields are explicitly classified as AI-assisted exploratory coding.
- Analysis and simulation parameters remain explicit so readers can edit them.
- Statistical results in manuscript prose should be generated at runtime. Any row classified as `statistical_result_literal` is a release blocker.
- Figure/table numbers, bibliography years, DOIs, layout dimensions, and formatting precision are not empirical findings.
