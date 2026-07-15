"""
Beyond GDP: Stock vs Flow National Power Analysis
拡張データセット — 交絡因子・広義ストック概念を含む

ストック概念（広義）:
  人的資本、都市鉱山・リサイクル資源、社会関係資本、制度資本、
  インフラ資本、文化資本、自然資本、技術蓄積、金融資本

フロー概念:
  貿易、軍事行動、外交活動、海外投資、移民、技術移転、文化輸出

データ由来:
  entity, period, era, region, regime_duration_yrs は歴史的事実を表すが、
  現行レコードには個別出典が紐付いていない。
  dominant, stock_index, trade_openness, geo_barrier, external_threat,
  relative_pop, tech_position, institutional_quality は公開データから算出した
  測定値ではない。2026-05-13の初回DevinセッションでAI支援により付与
  された探索的・主観的コーディング値であり、検証済みのexpert ratingでもない。
  closure_type, outcome, has_external_patron は歴史的事実に基づく分類を意図
  しているが、事前のcoding rule、レコード単位の出典、独立評価者検証はない。
"""

import csv
from pathlib import Path

import pandas as pd

DATASET_PROVENANCE = {
    "creation_session": "b8007b0c27d44f7a961387806de03a3a",
    "created_at_utc": "2026-05-13",
    "created_by": "AI-assisted assembly from user-supplied concepts, without user-supplied record values",
    "initial_records": 54,
    "expanded_records": 96,
    "record_level_sources_in_original_dataset": False,
    "independent_coders_in_original_dataset": 0,
}

SUBJECTIVE_AI_CODED_FIELDS = (
    "dominant",
    "stock_index",
    "trade_openness",
    "geo_barrier",
    "external_threat",
    "relative_pop",
    "tech_position",
    "institutional_quality",
)

HISTORICAL_CLASSIFICATION_FIELDS = (
    "closure_type",
    "outcome",
    "has_external_patron",
)

DATA_PATH = Path(__file__).resolve().parent / "data" / "polity_period_records.csv"

FLOAT_FIELDS = {
    "stock_index",
    "trade_openness",
    "geo_barrier",
    "external_threat",
    "relative_pop",
    "tech_position",
    "institutional_quality",
}
INT_FIELDS = {"regime_duration_yrs", "has_external_patron"}


def _load_records() -> list[dict[str, object]]:
    with DATA_PATH.open(encoding="utf-8") as file:
        records_from_csv = list(csv.DictReader(file))
    for record in records_from_csv:
        for field in FLOAT_FIELDS:
            record[field] = float(record[field])
        for field in INT_FIELDS:
            record[field] = int(record[field])
    if len(records_from_csv) != 96:
        raise ValueError(f"Expected 96 records, found {len(records_from_csv)}")
    return records_from_csv


records = _load_records()


def load_data():
    """DataFrameとして返す"""
    df = pd.DataFrame(records)
    df["dominant_binary"] = (df["dominant"] == "stock").astype(int)
    df["outcome_binary"] = (df["outcome"] == "overtaken").astype(int)
    # 中央値ベースの時代コード
    era_order = {
        "ancient": 0,
        "medieval": 1,
        "early_modern": 2,
        "modern": 3,
        "20c": 4,
        "contemporary": 5,
    }
    df["era_code"] = df["era"].map(era_order)
    df.attrs["dataset_provenance"] = DATASET_PROVENANCE
    df.attrs["subjective_ai_coded_fields"] = SUBJECTIVE_AI_CODED_FIELDS
    df.attrs["historical_classification_fields"] = HISTORICAL_CLASSIFICATION_FIELDS
    return df


if __name__ == "__main__":
    df = load_data()
    print(f"Total records: {len(df)}")
    print(f"\nDominant distribution:\n{df['dominant'].value_counts()}")
    print(f"\nOutcome distribution:\n{df['outcome'].value_counts()}")
    print(f"\nCross-tabulation:")
    print(pd.crosstab(df["dominant"], df["outcome"], margins=True))
