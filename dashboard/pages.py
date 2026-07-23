"""
Render functions for every dashboard page. Each function takes the
already-filtered DataFrame and renders directly into the current
Streamlit context. Kept separate from app.py so app.py stays a thin
router/shell.
"""
from __future__ import annotations

import streamlit as st

from dashboard.theme import KPI_CARD_HTML, SECTION_HTML
from src import queries as q
from utils import charts


def _section(title: str, subtitle: str = ""):
    st.markdown(SECTION_HTML.format(title=title, subtitle=subtitle), unsafe_allow_html=True)


def _kpi_row(items: list[tuple[str, str, str]]):
    """items: list of (icon, label, value)"""
    cols = st.columns(len(items))
    for col, (icon, label, value) in zip(cols, items):
        with col:
            st.markdown(KPI_CARD_HTML.format(icon=icon, label=label, value=value), unsafe_allow_html=True)


def page_overview(df):
    kpis = q.kpi_summary(df)
    _section("Executive Overview", "High-level snapshot of the current workforce")
    _kpi_row([
        ("👥", "Total Employees", f"{kpis['total_employees']:,}"),
        ("🎂", "Average Age", f"{kpis['avg_age']}"),
        ("🎓", "Avg Training Score", f"{kpis['avg_training_score']}"),
        ("⭐", "Avg Rating", f"{kpis['avg_rating']}"),
    ])
    st.write("")
    _kpi_row([
        ("🏢", "Departments", f"{kpis['n_departments']}"),
        ("🧭", "Avg Tenure (yrs)", f"{kpis['avg_service']}"),
        ("🏆", "KPI Achievement Rate", f"{kpis['promotion_rate']}%"),
        ("♀️", "Female Representation", f"{kpis['gender_ratio_female_pct']}%"),
    ])
    st.write("")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.bar_department_headcount(q.employees_by_department(df)),
                         width='stretch')
    with c2:
        st.plotly_chart(charts.pie_gender(q.gender_distribution(df)), width='stretch')

    st.plotly_chart(charts.treemap_department_region(df), width='stretch')


def page_employee_insights(df):
    _section("Employee Insights", "Distribution of age, tenure, and demographics")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.histogram(df, "age", "Age Distribution"), width='stretch')
    with c2:
        st.plotly_chart(charts.histogram(df, "length_of_service", "Length of Service Distribution"),
                         width='stretch')

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(charts.boxplot(df, "department", "age", "Age Spread by Department"),
                         width='stretch')
    with c4:
        st.plotly_chart(charts.sunburst_department_gender(df), width='stretch')

    st.subheader("🔍 Search Employee")
    emp_id = st.number_input("Employee ID", min_value=0, step=1, value=0)
    if emp_id:
        match = df[df["employee_id"] == emp_id]
        if match.empty:
            st.warning("No employee found with that ID in the current filtered view.")
        else:
            st.dataframe(match, width='stretch')


def page_performance(df):
    _section("Performance Analysis", "Ratings, KPI achievement, and score distributions")
    perf = q.department_performance(df)
    st.dataframe(perf, width='stretch')

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.area_department_performance(perf), width='stretch')
    with c2:
        st.plotly_chart(charts.violin(df, "department", "avg_training_score",
                                       "Training Score Distribution by Department"),
                         width='stretch')

    st.plotly_chart(charts.heatmap_correlation(q.correlation_matrix(df)), width='stretch')


def page_training(df):
    _section("Training Analysis", "Does training volume move the needle on scores and ratings?")
    train_df = q.training_effectiveness(df)
    st.plotly_chart(charts.line_training_effectiveness(train_df), width='stretch')

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.histogram(df, "avg_training_score", "Training Score Distribution"),
                         width='stretch')
    with c2:
        st.plotly_chart(charts.scatter(df, "no_of_trainings", "avg_training_score", "department",
                                        "Trainings Taken vs. Training Score"), width='stretch')
    st.dataframe(train_df, width='stretch')


def page_department(df):
    _section("Department Analysis", "Compare departments side by side")
    perf = q.department_performance(df)
    top, bottom = q.top_bottom_departments(df)
    st.plotly_chart(charts.bar_top_bottom_departments(top, bottom), width='stretch')
    st.dataframe(perf, width='stretch')


def page_retention(df):
    _section("Retention Analysis", "Tenure bands and how they relate to performance")
    ret_df = q.retention_metrics(df)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.bar_retention(ret_df), width='stretch')
    with c2:
        st.plotly_chart(charts.boxplot(df, "department", "length_of_service",
                                        "Tenure Spread by Department"), width='stretch')
    st.dataframe(ret_df, width='stretch')


def page_diversity(df):
    _section("Diversity Dashboard", "Gender balance across departments and regions")
    div_df = q.diversity_breakdown(df)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.pie_gender(q.gender_distribution(df)), width='stretch')
    with c2:
        st.plotly_chart(charts.sunburst_department_gender(df), width='stretch')
    st.dataframe(div_df, width='stretch')


def page_raw_data(df):
    _section("Raw Data", "Full filtered dataset")
    st.dataframe(df, width='stretch', height=520)
    st.caption(f"Showing {len(df):,} rows matching current filters.")


def page_downloads(df):
    from src.reports import to_csv_bytes, to_excel_bytes, to_pdf_summary_bytes
    _section("Download Reports", "Export the current filtered view")
    kpis = q.kpi_summary(df)
    dept_perf = q.department_performance(df)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("📄 Download CSV", data=to_csv_bytes(df),
                            file_name="employees_filtered.csv", mime="text/csv",
                            width='stretch')
    with c2:
        st.download_button("📊 Download Excel", data=to_excel_bytes(df, kpis),
                            file_name="employees_filtered.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            width='stretch')
    with c3:
        try:
            pdf_bytes = to_pdf_summary_bytes(kpis, dept_perf)
            st.download_button("🧾 Download PDF Summary", data=pdf_bytes,
                                file_name="management_report.pdf", mime="application/pdf",
                                width='stretch')
        except Exception as e:
            st.error(f"PDF generation failed: {e}")


def page_about():
    _section("About This Project", "")
    st.markdown("""
This dashboard is part of the **HR Analytics Platform** — an end-to-end project covering
data cleaning, a self-initializing database layer, reusable analytics functions, and an
interactive Plotly/Streamlit dashboard.

**Stack:** Python, Pandas, SQLAlchemy (SQLite/MySQL), Plotly, Streamlit, ReportLab.

See the project `README.md` for architecture details, setup instructions, and future
improvements.
""")
