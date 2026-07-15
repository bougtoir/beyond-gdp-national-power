#!/usr/bin/env python3
"""Inventory numeric literals and classify their reproducibility role."""

import ast
import csv
import re
from collections import Counter
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT = Path(__file__).resolve().parent / "numeric_literals.csv"
SUMMARY = Path(__file__).resolve().parent / "NUMERIC_LITERAL_AUDIT.md"
DATASET = PROJECT_DIR / "data" / "polity_period_records.csv"
NUMBER_IN_TEXT = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])")
SUBJECTIVE_FIELDS = {
    "stock_index",
    "trade_openness",
    "geo_barrier",
    "external_threat",
    "relative_pop",
    "tech_position",
    "institutional_quality",
}
HISTORICAL_FIELDS = {"period", "regime_duration_yrs", "has_external_patron"}


def _relative(path: Path) -> str:
    return path.relative_to(PROJECT_DIR).as_posix()


def _classify_code_literal(
    path: Path,
    context: str,
    literal_type: str,
) -> tuple[str, str, str]:
    relative = _relative(path)
    lower = context.lower()

    if literal_type == "number_embedded_in_text":
        if relative == "audit/audit_numeric_literals.py":
            return (
                "audit_implementation_literal",
                "low",
                "Pattern or label used by the numeric-audit implementation itself.",
            )
        if "{" in context and "}" in context:
            return (
                "dynamically_generated_value_or_format_precision",
                "low",
                "Number appears in an f-string or format specification; the reported value is generated at runtime.",
            )
        if any(token in lower for token in ("doi", "isbn", "http", "journal", "press", "university")):
            return (
                "bibliographic_or_source_number",
                "low",
                "Bibliographic, URL, edition, volume, page, or publication-year content.",
            )
        if any(token in lower for token in ("fig.", "figure", "table", "section", "level=")):
            return (
                "manuscript_structure_or_cross_reference",
                "low",
                "Figure, table, section, or heading number used for document structure.",
            )
        if any(
            token in lower
            for token in (
                "threshold",
                "axhline",
                "line2d",
                "always significant",
                "bootstrap 95",
                '"95% ci"',
            )
        ):
            return (
                "analysis_threshold_or_output_label",
                "medium",
                "Decision threshold, confidence-level label, or chart legend rather than a computed result.",
            )
        if any(token in lower for token in ("p =", "p <", "or =", "odds ratio", "conquest rate", "95% ci")):
            return (
                "statistical_result_literal",
                "high",
                "Statistical result is embedded in prose and should be generated from current analysis output.",
            )
        if any(token in lower for token in ("n =", "dataset of", "sample size", "records", "rows")):
            return (
                "sample_size_or_candidate_count_literal",
                "medium",
                "Count is embedded in prose or validation logic; manuscript counts should be generated dynamically.",
            )
        if any(token in lower for token in ("bc", "ad", "century", "since ", "period", "year", "histor")):
            return (
                "historical_date_or_prose_number",
                "low",
                "Historical date or contextual prose number, not a computed analysis result.",
            )
        return (
            "prose_or_label_number",
            "medium" if relative.startswith(("create_", "manuscript/")) else "low",
            "Number is embedded in a string and requires contextual review.",
        )

    if relative == "modern_analysis.py":
        return (
            "simulation_or_scenario_parameter",
            "medium",
            "Explicit forward-looking simulation or scenario assumption.",
        )
    if relative == "sensitivity_technical_network_exclusion.py":
        return (
            "candidate_definition_or_analysis_parameter",
            "medium",
            "Sensitivity-analysis definition, threshold, or coded scenario parameter.",
        )
    if relative in {"plot_sensitivity.py", "create_manuscript.py", "create_manuscript_latex.py"}:
        if any(
            token in lower
            for token in (
                "inch",
                "pt(",
                "cm(",
                "font",
                "figsize",
                "dpi",
                "linewidth",
                "width",
                "height",
                "margin",
                "slide",
                "cols=",
                "rows=",
                "level=",
                "color",
                "alpha=",
                "rotation",
                "space_",
            )
        ):
            return (
                "display_or_layout_constant",
                "low",
                "Document, chart, or slide layout constant.",
            )
    if any(
        token in lower
        for token in (
            "default_rng",
            "random_state",
            "n_boot",
            "percentile",
            "alpha",
            "threshold",
            "alternative=",
            "maxiter",
            "range(",
            "linspace",
            "arange",
            "reps",
            "seed",
        )
    ):
        return (
            "analysis_parameter_or_threshold",
            "medium",
            "Explicit analysis parameter, random seed, resampling count, or decision threshold.",
        )
    if relative == "data.py" and "expected" in lower:
        return (
            "input_validation_count",
            "low",
            "Dataset-shape assertion; protects the published canonical input from silent row loss.",
        )
    return (
        "code_constant_requires_context",
        "medium",
        "Numeric code constant not automatically reducible to a result, layout, or documented analysis parameter.",
    )


def _python_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(PROJECT_DIR.rglob("*.py")):
        if any(part in {".venv", "__pycache__", "springer-template"} for part in path.parts):
            continue
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, UnicodeDecodeError, SyntaxError) as error:
            rows.append(
                {
                    "file": _relative(path),
                    "line": getattr(error, "lineno", ""),
                    "field": "",
                    "value": "",
                    "literal_type": "parse_error",
                    "classification": "parse_error",
                    "review_priority": "high",
                    "context": str(error),
                    "reproducibility_note": "File could not be parsed and requires manual review.",
                }
            )
            continue

        lines = source.splitlines()
        for node in ast.walk(tree):
            values: list[tuple[object, str]] = []
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, (int, float))
                and not isinstance(node.value, bool)
            ):
                values.append((node.value, "numeric_ast_literal"))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                values.extend(
                    (match.group(), "number_embedded_in_text")
                    for match in NUMBER_IN_TEXT.finditer(node.value)
                )

            for value, literal_type in values:
                line = getattr(node, "lineno", 0)
                context = lines[line - 1].strip() if line else ""
                classification, priority, note = _classify_code_literal(
                    path, context, literal_type
                )
                rows.append(
                    {
                        "file": _relative(path),
                        "line": line,
                        "field": "",
                        "value": value,
                        "literal_type": literal_type,
                        "classification": classification,
                        "review_priority": priority,
                        "context": context,
                        "reproducibility_note": note,
                    }
                )
    return rows


def _dataset_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with DATASET.open(encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle))
    for row_number, record in enumerate(records, start=2):
        for field, value in record.items():
            if not NUMBER_IN_TEXT.fullmatch(value):
                continue
            if field in SUBJECTIVE_FIELDS:
                classification = "subjective_ai_assisted_input_value"
                note = (
                    "Published canonical input; retained from the legacy AI-assisted exploratory "
                    "coding and not calculated from a public dataset."
                )
                priority = "high"
            elif field in HISTORICAL_FIELDS:
                classification = "historically_anchored_input_value"
                note = (
                    "Published canonical historical input; field-level source status is documented "
                    "in supplementary_case_sources.csv."
                )
                priority = "medium"
            else:
                classification = "other_canonical_input_value"
                note = "Published canonical dataset input."
                priority = "medium"
            rows.append(
                {
                    "file": _relative(DATASET),
                    "line": row_number,
                    "field": field,
                    "value": value,
                    "literal_type": "canonical_csv_input",
                    "classification": classification,
                    "review_priority": priority,
                    "context": record["entity"],
                    "reproducibility_note": note,
                }
            )
    return rows


def main() -> None:
    rows = _python_rows() + _dataset_rows()
    rows.sort(
        key=lambda row: (
            str(row["file"]),
            int(row["line"]) if str(row["line"]).isdigit() else 0,
            str(row["field"]),
            str(row["value"]),
        )
    )
    fieldnames = [
        "file",
        "line",
        "field",
        "value",
        "literal_type",
        "classification",
        "review_priority",
        "context",
        "reproducibility_note",
    ]
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    classes = Counter(str(row["classification"]) for row in rows)
    priorities = Counter(str(row["review_priority"]) for row in rows)
    result_literals = [
        row for row in rows if row["classification"] == "statistical_result_literal"
    ]
    summary_lines = [
        "# Numeric Literal Audit",
        "",
        "This inventory separates canonical input values, subjective AI-assisted scores, "
        "analysis/scenario parameters, layout constants, historical/bibliographic numbers, "
        "dynamically generated manuscript values, and potentially hard-coded statistical results.",
        "",
        f"- Inventory rows: {len(rows)}",
        f"- High-priority rows: {priorities.get('high', 0)}",
        f"- Medium-priority rows: {priorities.get('medium', 0)}",
        f"- Statistical result literals requiring replacement: {len(result_literals)}",
        "",
        "## Classification counts",
        "",
        "| Classification | Rows |",
        "|---|---:|",
    ]
    summary_lines.extend(
        f"| `{name}` | {count} |" for name, count in sorted(classes.items())
    )
    summary_lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Values in `data/polity_period_records.csv` are deliberately published inputs, "
            "not hidden code constants. The subjective fields are explicitly classified as "
            "AI-assisted exploratory coding.",
            "- Analysis and simulation parameters remain explicit so readers can edit them.",
            "- Statistical results in manuscript prose should be generated at runtime. Any row "
            "classified as `statistical_result_literal` is a release blocker.",
            "- Figure/table numbers, bibliography years, DOIs, layout dimensions, and formatting "
            "precision are not empirical findings.",
        ]
    )
    SUMMARY.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} rows to {OUTPUT.relative_to(PROJECT_DIR)}")
    print("Statistical result literals requiring replacement:", len(result_literals))


if __name__ == "__main__":
    main()
