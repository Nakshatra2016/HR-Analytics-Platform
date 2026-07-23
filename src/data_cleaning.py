"""
Data cleaning utilities for the HR Analytics Platform.

Takes the raw exported CSV and produces an analysis-ready, deduplicated,
correctly-typed dataset. This is intentionally deterministic and logged
so every transformation is auditable.
"""
from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "employee_id", "department", "region", "education", "gender",
    "recruitment_channel", "no_of_trainings", "age", "previous_year_rating",
    "length_of_service", "KPIs_met_more_than_80", "awards_won",
    "avg_training_score",
]


def load_raw(csv_path) -> pd.DataFrame:
    """Load the raw CSV, raising a clear error if it's missing columns."""
    df = pd.read_csv(csv_path)
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Raw CSV is missing required columns: {sorted(missing)}")
    return df


def clean_employees(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full cleaning pipeline:
    - drop exact duplicate rows
    - drop duplicate employee_id (keep first occurrence)
    - fill/handle missing values sensibly per column
    - enforce correct dtypes
    - strip whitespace on string columns
    """
    df = df.copy()
    before = len(df)

    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="employee_id", keep="first")
    logger.info("Dropped %d duplicate rows", before - len(df))

    # String columns: strip whitespace, fill missing categorical values
    string_cols = ["department", "region", "education", "gender", "recruitment_channel"]
    for col in string_cols:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": None, "None": None})

    df["education"] = df["education"].fillna("Not Specified")
    df["department"] = df["department"].fillna("Unassigned")
    df["region"] = df["region"].fillna("Unknown")
    df["recruitment_channel"] = df["recruitment_channel"].fillna("other")
    df["gender"] = df["gender"].fillna("u")  # unknown

    # Numeric columns
    numeric_int_cols = ["no_of_trainings", "age", "length_of_service", "avg_training_score"]
    for col in numeric_int_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["employee_id", "age"])  # employee_id & age are non-negotiable

    # previous_year_rating has legitimate NaNs (new joiners with < 1 year service);
    # impute with the department median rather than dropping the row.
    df["previous_year_rating"] = pd.to_numeric(df["previous_year_rating"], errors="coerce")
    dept_median = df.groupby("department")["previous_year_rating"].transform("median")
    df["previous_year_rating"] = df["previous_year_rating"].fillna(dept_median)
    df["previous_year_rating"] = df["previous_year_rating"].fillna(df["previous_year_rating"].median())

    for col in numeric_int_cols:
        df[col] = df[col].fillna(df[col].median())

    # Final dtype enforcement
    df["employee_id"] = df["employee_id"].astype(int)
    df["no_of_trainings"] = df["no_of_trainings"].astype(int)
    df["age"] = df["age"].astype(int)
    df["length_of_service"] = df["length_of_service"].astype(int)
    df["avg_training_score"] = df["avg_training_score"].astype(int)
    df["previous_year_rating"] = df["previous_year_rating"].round().astype(int)
    df["KPIs_met_more_than_80"] = df["KPIs_met_more_than_80"].fillna(0).astype(int)
    df["awards_won"] = df["awards_won"].fillna(0).astype(int)

    # Sanity bounds (drop physically impossible rows rather than silently keep them)
    df = df[(df["age"] >= 18) & (df["age"] <= 70)]
    df = df[(df["avg_training_score"] >= 0) & (df["avg_training_score"] <= 100)]
    df = df[df["previous_year_rating"].between(1, 5)]

    df = df.sort_values("employee_id").reset_index(drop=True)
    return df[REQUIRED_COLUMNS]


def run_pipeline(raw_path, processed_path) -> pd.DataFrame:
    """Load raw -> clean -> write processed CSV -> return cleaned DataFrame."""
    df_raw = load_raw(raw_path)
    df_clean = clean_employees(df_raw)
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(processed_path, index=False)
    logger.info("Wrote %d cleaned rows to %s", len(df_clean), processed_path)
    return df_clean
