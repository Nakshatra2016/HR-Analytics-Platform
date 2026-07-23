"""Custom CSS injected into the Streamlit app for a premium look."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* App background */
.stApp {
    background: radial-gradient(circle at 10% 0%, #1e1b4b 0%, #0f172a 45%, #0b1120 100%);
}

/* Hide default Streamlit chrome */
#MainMenu, footer { visibility: hidden; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #14162b 0%, #0f172a 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* KPI card */
.kpi-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 18px 20px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(99,102,241,0.25);
    border-color: rgba(99,102,241,0.4);
}
.kpi-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #9CA3AF;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 28px;
    font-weight: 800;
    color: #F9FAFB;
}
.kpi-icon { font-size: 22px; margin-bottom: 4px; }

/* Section headers */
.section-title {
    font-size: 22px;
    font-weight: 700;
    color: #F9FAFB;
    margin: 8px 0 4px 0;
    border-left: 4px solid #6366F1;
    padding-left: 12px;
}
.section-sub {
    color: #9CA3AF;
    font-size: 13px;
    margin-bottom: 18px;
    padding-left: 16px;
}

/* Hero header */
.hero {
    background: linear-gradient(120deg, rgba(99,102,241,0.18), rgba(34,211,238,0.10));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 22px;
}
.hero-title { font-size: 30px; font-weight: 800; color: #F9FAFB; margin: 0; }
.hero-sub { color: #C7D2FE; font-size: 14px; margin-top: 6px; }

/* Buttons */
.stDownloadButton button, .stButton button {
    border-radius: 10px !important;
    border: 1px solid rgba(99,102,241,0.5) !important;
    background: linear-gradient(120deg, #6366F1, #8B5CF6) !important;
    color: white !important;
    font-weight: 600 !important;
}

/* Dataframe container */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
</style>
"""

KPI_CARD_HTML = """
<div class="kpi-card">
    <div class="kpi-icon">{icon}</div>
    <div class="kpi-label">{label}</div>
    <div class="kpi-value">{value}</div>
</div>
"""

SECTION_HTML = """
<div class="section-title">{title}</div>
<div class="section-sub">{subtitle}</div>
"""
