"""
HR Analytics Platform — main Streamlit entry point.

Run with:  streamlit run app.py

On first run this will automatically:
  1. clean the raw CSV into data/processed/employees_clean.csv (if needed)
  2. create the database + employees table (SQLite by default)
  3. seed the table from the cleaned CSV, skipping duplicates
No manual setup steps are required.
"""
from __future__ import annotations

import logging

import streamlit as st

from dashboard import pages
from dashboard.filters import render_filters
from dashboard.theme import CUSTOM_CSS
from src.database import ensure_ready
from utils.config import APP_ICON, APP_TITLE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide",
                    initial_sidebar_state="expanded")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(ttl=300, show_spinner=False)
def load_data():
    return ensure_ready()


def main():
    st.markdown(
        """
        <div class="hero">
            <p class="hero-title">📊 HR Analytics Platform</p>
            <p class="hero-sub">Employee performance, training, retention & diversity — in one interactive view</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Loading workforce data…"):
        try:
            df = load_data()
        except Exception as e:
            st.error(f"Failed to initialize data/database: {e}")
            logger.exception("Data initialization failed")
            st.stop()

    if df.empty:
        st.warning("No employee data available. Check data/raw/employees_raw.csv.")
        st.stop()

    st.sidebar.markdown(f"### {APP_ICON} {APP_TITLE}")
    page = st.sidebar.radio(
        "Navigate",
        [
            "Overview", "Employee Insights", "Performance Analysis", "Training Analysis",
            "Department Analysis", "Retention Analysis", "Diversity Dashboard",
            "Raw Data", "Download Reports", "About",
        ],
        label_visibility="collapsed",
    )

    filtered_df = render_filters(df)

    page_map = {
        "Overview": lambda: pages.page_overview(filtered_df),
        "Employee Insights": lambda: pages.page_employee_insights(filtered_df),
        "Performance Analysis": lambda: pages.page_performance(filtered_df),
        "Training Analysis": lambda: pages.page_training(filtered_df),
        "Department Analysis": lambda: pages.page_department(filtered_df),
        "Retention Analysis": lambda: pages.page_retention(filtered_df),
        "Diversity Dashboard": lambda: pages.page_diversity(filtered_df),
        "Raw Data": lambda: pages.page_raw_data(filtered_df),
        "Download Reports": lambda: pages.page_downloads(filtered_df),
        "About": pages.page_about,
    }

    if filtered_df.empty and page not in ("About",):
        st.info("No employees match the current filter combination. Try widening your filters.")
        return

    page_map[page]()


if __name__ == "__main__":
    main()
