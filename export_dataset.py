#!/usr/bin/env python3
"""Normalize the editable dataset CSV and export variable metadata."""

import csv
from pathlib import Path

from data import (
    HISTORICAL_CLASSIFICATION_FIELDS,
    SUBJECTIVE_AI_CODED_FIELDS,
    records,
)


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"


def export_records() -> None:
    output = DATA_DIR / "polity_period_records.csv"
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(records[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(records)


def export_metadata() -> None:
    factual_fields = {
        "entity",
        "period",
        "era",
        "region",
        "regime_duration_yrs",
    }
    output = DATA_DIR / "variable_metadata.csv"
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "field",
                "value_type",
                "origin",
                "public_data_derived",
                "record_level_source_in_original_dataset",
                "replacement_guidance",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for field in records[0]:
            if field in SUBJECTIVE_AI_CODED_FIELDS:
                value_type = "subjective_ai_assisted_legacy"
                origin = (
                    "AI-assisted exploratory coding on 2026-05-13; "
                    "not calculated from a public dataset"
                )
                replacement_guidance = (
                    "Edit this column in polity_period_records.csv and rerun reproduce.py"
                )
            elif field in HISTORICAL_CLASSIFICATION_FIELDS:
                value_type = "historically_anchored_classification"
                origin = "AI-assisted classification on 2026-05-13"
                replacement_guidance = (
                    "Review supplementary_case_sources.csv, edit the CSV, and rerun"
                )
            elif field in factual_fields:
                value_type = "historical_or_derived_factual_claim"
                origin = "AI-assisted entry on 2026-05-13"
                replacement_guidance = (
                    "Review supplementary_case_sources.csv, edit the CSV, and rerun"
                )
            else:
                value_type = "unclassified"
                origin = "AI-assisted entry on 2026-05-13"
                replacement_guidance = "Review before reuse"
            writer.writerow(
                {
                    "field": field,
                    "value_type": value_type,
                    "origin": origin,
                    "public_data_derived": "false",
                    "record_level_source_in_original_dataset": "false",
                    "replacement_guidance": replacement_guidance,
                }
            )


if __name__ == "__main__":
    export_records()
    export_metadata()
