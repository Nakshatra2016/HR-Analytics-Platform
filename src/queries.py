"""
Business logic / analytics computations.

Every function here takes a (already-filtered) DataFrame and returns
either a scalar KPI or a small summary DataFrame. Keeping these pure and
side-effect-free makes them trivially unit-testable and reusable across
every dashboard page.
"""
from __future__ import annotations

import pandas as pd


def kpi_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return {k: 0 for k in [
            "total_employees", "avg_age", "avg_training_score", "avg_rating",
            "avg_service", "promotion_rate", "gender_ratio_female_pct",
            "n_departments",
        ]}
    return {
        "total_employees": len(df),
        "avg_age": round(df["age"].mean(), 1),
        "avg_training_score": round(df["avg_training_score"].mean(), 1),
        "avg_rating": round(df["previous_year_rating"].mean(), 2),
        "avg_service": round(df["length_of_service"].mean(), 1),
        "promotion_rate": round(df["KPIs_met_more_than_80"].mean() * 100, 1),
        "gender_ratio_female_pct": round((df["gender"].str.lower() == "f").mean() * 100, 1),
        "n_departments": df["department"].nunique(),
    }


def employees_by_department(df: pd.DataFrame) -> pd.DataFrame:
    out = df["department"].value_counts().reset_index()
    out.columns = ["department", "count"]
    return out.sort_values("count", ascending=False)


def employees_by_region(df: pd.DataFrame) -> pd.DataFrame:
    out = df["region"].value_counts().reset_index()
    out.columns = ["region", "count"]
    return out.sort_values("count", ascending=False)


def gender_distribution(df: pd.DataFrame) -> pd.DataFrame:
    out = df["gender"].value_counts().reset_index()
    out.columns = ["gender", "count"]
    return out


def department_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Avg rating / training score / KPI-met rate / awards per department."""
    grp = df.groupby("department").agg(
        avg_rating=("previous_year_rating", "mean"),
        avg_training_score=("avg_training_score", "mean"),
        kpi_met_pct=("KPIs_met_more_than_80", "mean"),
        awards_pct=("awards_won", "mean"),
        headcount=("employee_id", "count"),
    ).reset_index()
    grp["avg_rating"] = grp["avg_rating"].round(2)
    grp["avg_training_score"] = grp["avg_training_score"].round(1)
    grp["kpi_met_pct"] = (grp["kpi_met_pct"] * 100).round(1)
    grp["awards_pct"] = (grp["awards_pct"] * 100).round(1)
    return grp.sort_values("avg_rating", ascending=False)


def training_effectiveness(df: pd.DataFrame) -> pd.DataFrame:
    """Does more training correlate with higher scores/ratings?"""
    grp = df.groupby("no_of_trainings").agg(
        avg_training_score=("avg_training_score", "mean"),
        avg_rating=("previous_year_rating", "mean"),
        headcount=("employee_id", "count"),
    ).reset_index()
    grp["avg_training_score"] = grp["avg_training_score"].round(1)
    grp["avg_rating"] = grp["avg_rating"].round(2)
    return grp.sort_values("no_of_trainings")


def retention_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Bucket employees by tenure to approximate a retention/service curve."""
    bins = [0, 2, 5, 10, 15, 100]
    labels = ["0-2 yrs", "3-5 yrs", "6-10 yrs", "11-15 yrs", "15+ yrs"]
    tmp = df.copy()
    tmp["tenure_band"] = pd.cut(tmp["length_of_service"], bins=bins, labels=labels, right=True)
    grp = tmp.groupby("tenure_band", observed=True).agg(
        headcount=("employee_id", "count"),
        avg_rating=("previous_year_rating", "mean"),
        avg_training_score=("avg_training_score", "mean"),
    ).reset_index()
    grp["avg_rating"] = grp["avg_rating"].round(2)
    grp["avg_training_score"] = grp["avg_training_score"].round(1)
    return grp


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = [
        "age", "no_of_trainings", "previous_year_rating", "length_of_service",
        "avg_training_score", "KPIs_met_more_than_80", "awards_won",
    ]
    return df[numeric_cols].corr().round(2)


def top_bottom_departments(df: pd.DataFrame, n: int = 3):
    perf = department_performance(df)
    return perf.head(n), perf.tail(n)


def diversity_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby(["department", "gender"]).size().reset_index(name="count")
    return grp
