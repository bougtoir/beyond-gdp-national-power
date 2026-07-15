"""Build the record-level source supplement from the reviewed source catalog."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

PROJECT_DIR = Path(__file__).resolve().parents[1]
AUDIT_DIR = PROJECT_DIR / "audit"
sys.path.insert(0, str(PROJECT_DIR))

from data import load_data


CATALOG_PATH = AUDIT_DIR / "case_source_catalog.csv"
SUPPLEMENT_PATH = AUDIT_DIR / "supplementary_case_sources.csv"
APPLICABILITY_PATH = AUDIT_DIR / "public_dataset_applicability.csv"
CURRENT_YEAR = 2026

DATASETS = {
    "Seshat Cliopatria": {
        "url": "https://zenodo.org/records/13363121",
        "start": -3400,
        "end": 2024,
        "role": "Polity names, spatial extent, and chronology",
    },
    "Maddison Project Database 2023": {
        "url": "https://doi.org/10.34894/INZBF2",
        "start": 1,
        "end": 2022,
        "role": "Country and regional population and GDP estimates",
    },
    "Clio-Infra": {
        "url": "https://clio-infra.eu/",
        "start": 1500,
        "end": 2013,
        "role": "Historical economic, social, institutional, and conflict indicators",
    },
    "HYDE": {
        "url": "https://www.pbl.nl/en/hyde-history-database-of-the-global-environment",
        "start": -10000,
        "end": 2020,
        "role": "Gridded population and land-use context, not polity coding",
    },
    "V-Dem v16": {
        "url": "https://v-dem.net/data/the-v-dem-dataset/country-year-v-dem-core-v16/",
        "start": 1789,
        "end": 2025,
        "role": "Modern country-year political institutions",
    },
    "Correlates of War Formal Alliances v4.1": {
        "url": "https://correlatesofwar.org/data-sets/formal-alliances/",
        "start": 1816,
        "end": 2012,
        "role": "Formal interstate alliances; not a direct patron measure",
    },
    "Polity5": {
        "url": "https://systemicpeace.org/inscrdata.html",
        "start": 1800,
        "end": 2018,
        "role": "Modern regime authority and transition dates",
    },
}

FIELDNAMES = [
    "record_id",
    "entity",
    "period",
    "field",
    "current_value",
    "verification_status",
    "source_title",
    "source_author_or_institution",
    "source_url",
    "source_locator",
    "source_excerpt",
    "accessed_at_utc",
    "coding_note",
    "applicable_auxiliary_datasets",
]


def _parse_period(period: str) -> tuple[int, int]:
    match = re.fullmatch(r"(BC|AD)(\d+)-(BC|AD)(\d+|現在)", period)
    if not match:
        raise ValueError(f"Unsupported period: {period}")
    start_era, start_year, end_era, end_year = match.groups()
    start = -int(start_year) if start_era == "BC" else int(start_year)
    end = CURRENT_YEAR if end_year == "現在" else int(end_year)
    if end_era == "BC":
        end = -end
    return start, end


def _applicable_datasets(period: str) -> list[str]:
    start, end = _parse_period(period)
    return [
        name
        for name, metadata in DATASETS.items()
        if start <= metadata["end"] and end >= metadata["start"]
    ]


def _load_catalog() -> dict[str, dict[str, str]]:
    with CATALOG_PATH.open(encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    if len(rows) != 96:
        raise ValueError(f"Expected 96 catalog records, found {len(rows)}")
    catalog = {row["entity"]: row for row in rows}
    if len(catalog) != 96:
        raise ValueError("Duplicate entities in source catalog")
    return catalog


def _source_row(
    record_id: int,
    entity: str,
    period: str,
    field: str,
    current_value: object,
    status: str,
    title: str,
    url: str,
    excerpt: str,
    accessed_at: str,
    note: str,
    applicable: list[str],
) -> dict[str, object]:
    hostname = urlparse(url).netloc.lower().removeprefix("www.")
    institutions = {
        "britannica.com": "Encyclopaedia Britannica",
        "kids.britannica.com": "Encyclopaedia Britannica",
        "cambridge.org": "Cambridge University Press",
        "jstage.jst.go.jp": "Japan Science and Technology Agency",
        "brill.com": "Brill",
        "sciencedirect.com": "Elsevier",
        "tandfonline.com": "Taylor & Francis",
        "academic.oup.com": "Oxford University Press",
        "nids.mod.go.jp": "National Institute for Defense Studies, Japan",
        "amview.japan.usembassy.gov": "U.S. Embassy in Japan",
        "congress.gov": "Congressional Research Service",
        "govinfo.gov": "U.S. Government Publishing Office",
        "pennpress.org": "University of Pennsylvania Press",
        "cup.columbia.edu": "Columbia University Press",
        "history.state.gov": "Office of the Historian, U.S. Department of State",
        "frontiersin.org": "Frontiers",
        "ideas.repec.org": "Research Papers in Economics",
        "persee.fr": "Persée",
        "web.archive.org": "Encyclopaedia Britannica archived by the Internet Archive",
        "unire.unige.it": "University of Genoa",
        "press.princeton.edu": "Princeton University Press",
        "press.umich.edu": "University of Michigan Press",
        "degruyterbrill.com": "De Gruyter Brill",
        "bmlv.gv.at": "Austrian Federal Ministry of Defence",
        "asianstudies.org": "Association for Asian Studies",
        "aeaweb.org": "American Economic Association",
        "usvietnam.uoregon.edu": "University of Oregon",
        "biblio.ugent.be": "Ghent University",
        "emandulo.apc.uct.ac.za": "University of Cape Town",
        "moodle2.units.it": "University of Trieste",
        "books.google.com": "Google Books catalog record",
        "hdl.handle.net": "Handle repository record",
    }
    institution = institutions.get(hostname, hostname)
    if hostname == "doi.org":
        doi_publishers = {
            "10.1017": "Cambridge University Press",
            "10.1163": "Brill",
            "10.4324": "Routledge",
            "10.1353": "Project MUSE",
            "10.1162": "MIT Press",
            "10.23943": "Princeton University Press",
            "10.1093": "Oxford University Press",
            "10.1111": "Wiley",
            "10.1080": "Taylor & Francis",
            "10.1177": "SAGE",
            "10.1007": "Springer",
            "10.1142": "World Scientific",
            "10.16912": "The Korean History Review",
        }
        doi = urlparse(url).path.lstrip("/")
        institution = next(
            (
                publisher
                for prefix, publisher in doi_publishers.items()
                if doi.startswith(prefix)
            ),
            "DOI-registered scholarly publication",
        )
    return {
        "record_id": record_id,
        "entity": entity,
        "period": period,
        "field": field,
        "current_value": current_value,
        "verification_status": status,
        "source_title": title,
        "source_author_or_institution": institution,
        "source_url": url,
        "source_locator": "Article, chapter, or dataset overview; relevant text is reproduced in source_excerpt",
        "source_excerpt": excerpt,
        "accessed_at_utc": accessed_at,
        "coding_note": note,
        "applicable_auxiliary_datasets": "; ".join(applicable),
    }


def build_supplement() -> None:
    catalog = _load_catalog()
    data = load_data()
    rows: list[dict[str, object]] = []
    applicability_rows: list[dict[str, object]] = []

    for record_id, record in enumerate(data.to_dict("records"), start=1):
        entity = record["entity"]
        period = record["period"]
        source = catalog[entity]
        applicable = _applicable_datasets(period)
        general = (
            source["general_source_title"],
            source["general_source_url"],
            source["general_source_excerpt"],
        )

        rows.append(
            _source_row(
                record_id,
                entity,
                period,
                "entity",
                entity,
                "supported_by_reference_overview",
                *general,
                source["accessed_at_utc"],
                "The cited reference identifies the polity or political unit.",
                applicable,
            )
        )
        rows.append(
            _source_row(
                record_id,
                entity,
                period,
                "period",
                period,
                "polity_chronology_supported_project_window_interpretive",
                *general,
                source["accessed_at_utc"],
                "The source supports the polity chronology; split periods and policy windows are project-defined analytical intervals.",
                applicable,
            )
        )

        if record["closure_type"] == "none":
            closure_source = general
        else:
            closure_source = (
                source["closure_source_title"],
                source["closure_source_url"],
                source["closure_source_excerpt"],
            )
        rows.append(
            _source_row(
                record_id,
                entity,
                period,
                "closure_type",
                record["closure_type"],
                source["closure_assessment"],
                *closure_source,
                source["accessed_at_utc"],
                source["closure_note"],
                applicable,
            )
        )

        outcome_status = "historical_event_supported_category_is_project_interpretation"
        outcome_note = (
            "The source documents the polity history or terminal event. The three-category "
            "outcome is an AI-assisted project classification rather than a source variable."
        )
        if entity == "ハンザ同盟":
            outcome_status = "classification_contested_decline_not_conquest"
            outcome_note = (
                "The source describes long decline and institutional eclipse, not a discrete "
                "conquest; overtaken requires revision or an explicit coding rule."
            )
        elif entity == "エチオピア帝国":
            outcome_status = "classification_contested_occupation_and_restoration"
            outcome_note = (
                "Italian occupation began in 1936 and Ethiopian sovereignty was restored in "
                "1941; survived depends on whether temporary occupation counts as disruption."
            )
        outcome_source = general
        if source.get("outcome_source_url"):
            outcome_source = (
                source["outcome_source_title"],
                source["outcome_source_url"],
                source["outcome_source_excerpt"],
            )
        rows.append(
            _source_row(
                record_id,
                entity,
                period,
                "outcome",
                record["outcome"],
                outcome_status,
                *outcome_source,
                source["accessed_at_utc"],
                outcome_note,
                applicable,
            )
        )

        if record["has_external_patron"]:
            patron_source = (
                source["patron_source_title"],
                source["patron_source_url"],
                source["patron_source_excerpt"],
            )
        else:
            patron_source = general
        rows.append(
            _source_row(
                record_id,
                entity,
                period,
                "has_external_patron",
                record["has_external_patron"],
                source["patron_assessment"],
                *patron_source,
                source["accessed_at_utc"],
                source["patron_note"],
                applicable,
            )
        )

        start, end = _parse_period(period)
        applicability_rows.append(
            {
                "record_id": record_id,
                "entity": entity,
                "period": period,
                **{
                    name: int(start <= metadata["end"] and end >= metadata["start"])
                    for name, metadata in DATASETS.items()
                },
            }
        )

    if len(rows) != 480:
        raise ValueError(f"Expected 480 source rows, found {len(rows)}")
    if any(not row["source_url"] or not row["source_title"] for row in rows):
        raise ValueError("Every source row must have a title and URL")

    with SUPPLEMENT_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=FIELDNAMES, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)

    applicability_fields = ["record_id", "entity", "period", *DATASETS]
    with APPLICABILITY_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=applicability_fields, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(applicability_rows)

    print(f"Wrote {len(rows)} rows to {SUPPLEMENT_PATH.relative_to(PROJECT_DIR)}")
    print(
        f"Wrote {len(applicability_rows)} rows to "
        f"{APPLICABILITY_PATH.relative_to(PROJECT_DIR)}"
    )


if __name__ == "__main__":
    build_supplement()
