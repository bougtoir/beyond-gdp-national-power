"""Probe source-catalog URLs without treating access failures as invalid citations."""

from __future__ import annotations

import csv
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path


AUDIT_DIR = Path(__file__).resolve().parent
CATALOG_PATH = AUDIT_DIR / "case_source_catalog.csv"
OUTPUT_PATH = AUDIT_DIR / "source_url_status.csv"
URL_FIELDS = (
    "general_source_url",
    "closure_source_url",
    "outcome_source_url",
    "patron_source_url",
)
OUTPUT_FIELDS = ("url", "http_status", "final_url", "error", "checked_at_utc")


def _probe(url: str) -> dict[str, str]:
    checked_at = datetime.now(timezone.utc).isoformat()
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 reproducibility-audit/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return {
                "url": url,
                "http_status": str(response.status),
                "final_url": response.url,
                "error": "",
                "checked_at_utc": checked_at,
            }
    except urllib.error.HTTPError as error:
        return {
            "url": url,
            "http_status": str(error.code),
            "final_url": error.geturl(),
            "error": f"HTTPError: {error.reason}",
            "checked_at_utc": checked_at,
        }
    except Exception as error:
        return {
            "url": url,
            "http_status": "",
            "final_url": "",
            "error": f"{type(error).__name__}: {error}",
            "checked_at_utc": checked_at,
        }


def main() -> None:
    with CATALOG_PATH.open(encoding="utf-8", newline="") as file:
        catalog = list(csv.DictReader(file))

    urls = sorted(
        {
            row[field].strip()
            for row in catalog
            for field in URL_FIELDS
            if row[field].strip()
        }
    )
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(_probe, urls))

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=OUTPUT_FIELDS, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(results)

    status_counts: dict[str, int] = {}
    for result in results:
        status = result["http_status"] or "ERROR"
        status_counts[status] = status_counts.get(status, 0) + 1
    print(f"Wrote {len(results)} URL checks to {OUTPUT_PATH}")
    print(f"Status counts: {status_counts}")


if __name__ == "__main__":
    main()
