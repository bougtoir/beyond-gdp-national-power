#!/usr/bin/env python3
"""Generate record-level lineage tables from the repository history."""

import ast
import csv
import subprocess
from collections import Counter
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = PROJECT_DIR.parent
OUTPUT_DIR = Path(__file__).resolve().parent

REVISIONS = {
    "initial_54": "f3309fd92ba79a6b1cff50a9c215edf0364eea88",
    "expanded_96": "e268fdac4f4fa339a903df5a687522c9e9a88359",
    "three_category": "4fd95f82b6e4f40b1f3e8cc9d7f5986a548e43d6",
    "borderline_branch": "b9dbb9c",
}

NUMERIC_CODING_FIELDS = [
    "stock_index",
    "trade_openness",
    "geo_barrier",
    "external_threat",
    "relative_pop",
    "tech_position",
    "institutional_quality",
]


def records_at(revision: str) -> list[dict]:
    source = subprocess.check_output(
        [
            "git",
            "show",
            f"{revision}:beyond-gdp-national-power/data.py",
        ],
        cwd=REPO_DIR,
        text=True,
    )
    tree = ast.parse(source)
    assignment = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "records" for target in node.targets)
    )
    return ast.literal_eval(assignment.value)


def by_entity(records: list[dict]) -> dict[str, dict]:
    return {record["entity"]: record for record in records}


def generate_record_lineage() -> None:
    versions = {name: records_at(revision) for name, revision in REVISIONS.items()}
    indexed = {name: by_entity(records) for name, records in versions.items()}
    initial_entities = set(indexed["initial_54"])

    fieldnames = [
        "entity",
        "period",
        "cohort",
        "introduced_commit",
        "original_outcome",
        "three_category_outcome",
        "borderline_branch_outcome",
        "current_master_outcome",
        "outcome_changed_on_borderline_branch",
        "record_level_source",
        "coding_rubric",
        "independent_coders",
    ]

    current = by_entity(records_at("master"))
    output = OUTPUT_DIR / "record_lineage.csv"
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fieldnames, lineterminator="\n"
        )
        writer.writeheader()
        for record in versions["expanded_96"]:
            entity = record["entity"]
            cohort = "initial_54" if entity in initial_entities else "power_target_addition_42"
            original = indexed["expanded_96"][entity]["outcome"]
            three_category = indexed["three_category"][entity]["outcome"]
            borderline = indexed["borderline_branch"][entity]["outcome"]
            writer.writerow(
                {
                    "entity": entity,
                    "period": record["period"],
                    "cohort": cohort,
                    "introduced_commit": (
                        REVISIONS["initial_54"]
                        if cohort == "initial_54"
                        else REVISIONS["expanded_96"]
                    ),
                    "original_outcome": original,
                    "three_category_outcome": three_category,
                    "borderline_branch_outcome": borderline,
                    "current_master_outcome": current[entity]["outcome"],
                    "outcome_changed_on_borderline_branch": borderline != three_category,
                    "record_level_source": "not_present_in_data.py_or_session_log",
                    "coding_rubric": "not_present_in_repository_or_session_log",
                    "independent_coders": "not_documented",
                }
            )


def generate_numeric_summary() -> None:
    records = records_at("master")
    output = OUTPUT_DIR / "numeric_coding_summary.csv"
    fieldnames = [
        "field",
        "record_count",
        "unique_value_count",
        "unique_values",
        "count_on_0_05_grid",
        "record_level_source",
        "coding_rubric",
    ]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fieldnames, lineterminator="\n"
        )
        writer.writeheader()
        for field in NUMERIC_CODING_FIELDS:
            values = [record[field] for record in records]
            counts = Counter(values)
            writer.writerow(
                {
                    "field": field,
                    "record_count": len(values),
                    "unique_value_count": len(counts),
                    "unique_values": " ".join(str(value) for value in sorted(counts)),
                    "count_on_0_05_grid": sum(
                        abs(value * 20 - round(value * 20)) < 1e-9 for value in values
                    ),
                    "record_level_source": "not_present_in_data.py_or_session_log",
                    "coding_rubric": "not_present_in_repository_or_session_log",
                }
            )


if __name__ == "__main__":
    generate_record_lineage()
    generate_numeric_summary()
