#!/usr/bin/env python3
"""Run the complete public analysis pipeline in dependency order."""

import csv
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
SCRIPTS = [
    "data.py",
    "export_dataset.py",
    "audit/build_supplementary_sources.py",
    "audit/audit_numeric_literals.py",
    "analysis.py",
    "mediation.py",
    "serial_mediation.py",
    "modern_analysis.py",
    "sensitivity_technical_network_exclusion.py",
    "plot_sensitivity.py",
    "causal_analysis.py",
    "create_manuscript.py",
    "create_manuscript_latex.py",
]
EXPECTED_CSV_ROWS = {
    "data/polity_period_records.csv": 96,
    "data/variable_metadata.csv": 16,
    "audit/supplementary_case_sources.csv": 480,
    "audit/public_dataset_applicability.csv": 96,
}
EXPECTED_OUTPUTS = [
    "audit/numeric_literals.csv",
    "audit/NUMERIC_LITERAL_AUDIT.md",
    "audit/PROVENANCE_AUDIT.md",
    "audit/REVIEWER_PERSPECTIVE_AUDIT.md",
    "audit/EEH_SUBMISSION_COMPLIANCE.md",
    "audit/SOURCE_URL_AUDIT.md",
    "manuscript/manuscript.docx",
    "manuscript/manuscript.tex",
    "manuscript/table_s1.docx",
    "manuscript/table_s1.tex",
    "manuscript/highlights.docx",
    "manuscript/cover_letter.docx",
    "manuscript/cover_letter.tex",
    "manuscript/references.bib",
    "manuscript/figures_pptx.pptx",
    "manuscript/figures/Fig1.png",
    "manuscript/figures/Fig2.png",
    "manuscript/figures/Fig3.png",
    "manuscript/figures/Fig4.png",
]
FORBIDDEN_TEXT = [
    "/" + "/".join(["home", "ubuntu", "repos", "wip"]),
    "/" + "/".join(["home", "ubuntu", "britannica_search_results"]),
    "/" + "/".join(["home", "ubuntu", "classification_search_results"]),
    "/" + "/".join(["home", "ubuntu", "cliopatria"]),
    "wiki" + "pedia",
]
EXCLUDED_SCAN_DIRECTORIES = {".git", ".venv", "venv", "__pycache__"}


def _csv_row_count(relative_path: str) -> int:
    with (PROJECT_DIR / relative_path).open(encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def verify_outputs() -> None:
    for relative_path, expected_rows in EXPECTED_CSV_ROWS.items():
        actual_rows = _csv_row_count(relative_path)
        if actual_rows != expected_rows:
            raise RuntimeError(
                f"{relative_path}: expected {expected_rows} rows, found {actual_rows}"
            )
    missing = [
        relative_path
        for relative_path in EXPECTED_OUTPUTS
        if not (PROJECT_DIR / relative_path).is_file()
    ]
    if missing:
        raise RuntimeError(f"Missing expected outputs: {', '.join(missing)}")

    source_extensions = {".py", ".md", ".csv", ".tex", ".bib", ".yml", ".yaml"}
    for path in PROJECT_DIR.rglob("*"):
        relative_path = path.relative_to(PROJECT_DIR)
        if (
            not path.is_file()
            or any(part in EXCLUDED_SCAN_DIRECTORIES for part in relative_path.parts)
            or path.suffix.lower() not in source_extensions
            or "springer-template" in path.parts
        ):
            continue
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        for forbidden in FORBIDDEN_TEXT:
            if forbidden.lower() in text:
                raise RuntimeError(f"Forbidden text {forbidden!r} found in {path}")
    print("\nValidated canonical row counts, expected outputs, and public-only paths.")


def main() -> None:
    for script in SCRIPTS:
        print(f"\n=== {script} ===", flush=True)
        subprocess.run(
            [sys.executable, script],
            cwd=PROJECT_DIR,
            check=True,
        )
    verify_outputs()


if __name__ == "__main__":
    main()
