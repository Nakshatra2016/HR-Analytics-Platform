"""
Reusable Plotly chart builders with a consistent professional theme.

Every function returns a `plotly.graph_objects.Figure` — nothing here
touches Streamlit directly, so these are testable and reusable outside
the dashboard too (e.g. in the notebook or a report generator).
"""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

PALETTE = ["#6366F1", "#22D3EE", "#F472B6", "#34D399", "#FBBF24",
           "#A78BFA", "#FB7185", "#60A5FA", "#4ADE80", "#F97316"]

TEMPLATE_LAYOUT = dict(
    font=dict(family="Inter, -apple-system, Segoe UI, sans-serif", size=13, color="#E5E7EB"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=30, r=20, t=60, b=30),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    title=dict(font=dict(size=17, color="#F9FAFB")),
    hoverlabel=dict(bgcolor="#1F2937", font_size=12, font_family="Inter"),
)


def _style(fig: go.Figure) -> go.Figure:
    fig.update_layout(**TEMPLATE_LAYOUT)
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.1)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.1)")
    return fig


def bar_department_headcount(dept_df: pd.DataFrame) -> go.Figure:
    fig = px.bar(dept_df, x="department", y="count", color="count",
                 color_continuous_scale=[PALETTE[0], PALETTE[2]],
                 title="Employees by Department")
    return _style(fig)


def pie_gender(gender_df: pd.DataFrame) -> go.Figure:
    fig = px.pie(gender_df, names="gender", values="count", hole=0.45,
                 color_discrete_sequence=PALETTE, title="Gender Distribution")
    return _style(fig)


def histogram(df: pd.DataFrame, col: str, title: str, nbins: int = 20) -> go.Figure:
    fig = px.histogram(df, x=col, nbins=nbins, color_discrete_sequence=[PALETTE[1]], title=title)
    return _style(fig)


def treemap_department_region(df: pd.DataFrame) -> go.Figure:
    grp = df.groupby(["department", "region"]).size().reset_index(name="count")
    fig = px.treemap(grp, path=["department", "region"], values="count",
                      color="count", color_continuous_scale=[PALETTE[0], PALETTE[3]],
                      title="Department → Region Headcount Treemap")
    return _style(fig)


def sunburst_department_gender(df: pd.DataFrame) -> go.Figure:
    grp = df.groupby(["department", "gender"]).size().reset_index(name="count")
    fig = px.sunburst(grp, path=["department", "gender"], values="count",
                       color_discrete_sequence=PALETTE, title="Department → Gender Breakdown")
    return _style(fig)


def heatmap_correlation(corr_df: pd.DataFrame) -> go.Figure:
    fig = px.imshow(corr_df, text_auto=True, color_continuous_scale="RdBu_r",
                     aspect="auto", title="Correlation Matrix — Numeric Features")
    return _style(fig)


def boxplot(df: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    fig = px.box(df, x=x, y=y, color=x, color_discrete_sequence=PALETTE, title=title)
    fig.update_layout(showlegend=False)
    return _style(fig)


def violin(df: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    fig = px.violin(df, x=x, y=y, color=x, box=True, points=False,
                     color_discrete_sequence=PALETTE, title=title)
    fig.update_layout(showlegend=False)
    return _style(fig)


def scatter(df: pd.DataFrame, x: str, y: str, color: str, title: str) -> go.Figure:
    fig = px.scatter(df, x=x, y=y, color=color, opacity=0.7,
                      color_discrete_sequence=PALETTE, title=title)
    return _style(fig)


def line_training_effectiveness(train_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=train_df["no_of_trainings"], y=train_df["avg_training_score"],
                              mode="lines+markers", name="Avg Training Score",
                              line=dict(color=PALETTE[0], width=3)))
    fig.add_trace(go.Scatter(x=train_df["no_of_trainings"], y=train_df["avg_rating"] * 20,
                              mode="lines+markers", name="Avg Rating (x20 scaled)",
                              line=dict(color=PALETTE[2], width=3, dash="dot")))
    fig.update_layout(title="Training Volume vs. Score & Rating")
    return _style(fig)


def area_department_performance(perf_df: pd.DataFrame) -> go.Figure:
    fig = px.area(perf_df.sort_values("avg_rating"), x="department", y="avg_rating",
                   color_discrete_sequence=[PALETTE[3]], title="Average Rating by Department")
    return _style(fig)


def bar_retention(retention_df: pd.DataFrame) -> go.Figure:
    fig = px.bar(retention_df, x="tenure_band", y="headcount", color="tenure_band",
                 color_discrete_sequence=PALETTE, title="Headcount by Tenure Band")
    fig.update_layout(showlegend=False)
    return _style(fig)


def bar_top_bottom_departments(top_df: pd.DataFrame, bottom_df: pd.DataFrame) -> go.Figure:
    top_df = top_df.assign(group="Top Performing")
    bottom_df = bottom_df.assign(group="Needs Attention")
    combined = pd.concat([top_df, bottom_df])
    fig = px.bar(combined, x="department", y="avg_rating", color="group",
                 color_discrete_map={"Top Performing": PALETTE[3], "Needs Attention": PALETTE[6]},
                 title="Top vs. Lowest Performing Departments (by Avg Rating)")
    return _style(fig)
