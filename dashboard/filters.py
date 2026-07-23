"""Sidebar filter widgets. Applies instantly (no submit button needed,
since Streamlit reruns on every widget interaction)."""
from __future__ import annotations

import streamlit as st
import pandas as pd


def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown("## 🔎 Filters")

    department = st.sidebar.multiselect("Department", sorted(df["department"].dropna().unique()))
    region = st.sidebar.multiselect("Region", sorted(df["region"].dropna().unique()))
    gender = st.sidebar.multiselect("Gender", sorted(df["gender"].dropna().unique()))
    education = st.sidebar.multiselect("Education", sorted(df["education"].dropna().unique()))
    channel = st.sidebar.multiselect("Recruitment Channel", sorted(df["recruitment_channel"].dropna().unique()))

    age_min, age_max = int(df["age"].min()), int(df["age"].max())
    age_range = st.sidebar.slider("Age Range", age_min, age_max, (age_min, age_max))

    rating_min, rating_max = int(df["previous_year_rating"].min()), int(df["previous_year_rating"].max())
    rating_range = st.sidebar.slider("Performance Rating", rating_min, rating_max, (rating_min, rating_max))

    score_min, score_max = int(df["avg_training_score"].min()), int(df["avg_training_score"].max())
    score_range = st.sidebar.slider("Training Score", score_min, score_max, (score_min, score_max))

    service_min, service_max = int(df["length_of_service"].min()), int(df["length_of_service"].max())
    service_range = st.sidebar.slider("Length of Service", service_min, service_max, (service_min, service_max))

    awards_only = st.sidebar.checkbox("Awarded employees only", value=False)
    kpi_only = st.sidebar.checkbox("KPI > 80% achievers only", value=False)

    out = df.copy()
    if department:
        out = out[out["department"].isin(department)]
    if region:
        out = out[out["region"].isin(region)]
    if gender:
        out = out[out["gender"].isin(gender)]
    if education:
        out = out[out["education"].isin(education)]
    if channel:
        out = out[out["recruitment_channel"].isin(channel)]

    out = out[out["age"].between(*age_range)]
    out = out[out["previous_year_rating"].between(*rating_range)]
    out = out[out["avg_training_score"].between(*score_range)]
    out = out[out["length_of_service"].between(*service_range)]

    if awards_only:
        out = out[out["awards_won"] == 1]
    if kpi_only:
        out = out[out["KPIs_met_more_than_80"] == 1]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"**{len(out):,}** of {len(df):,} employees match current filters.")

    if st.sidebar.button("♻️ Reset Filters", width='stretch'):
        st.rerun()

    return out
