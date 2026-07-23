"""
Report generation: turns a (filtered) employee DataFrame + KPI summary into
downloadable CSV, Excel, and PDF artifacts. Used by the Streamlit
"Download Reports" page.
"""
from __future__ import annotations

import io
from datetime import datetime

import pandas as pd


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def to_excel_bytes(df: pd.DataFrame, kpis: dict | None = None) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Employee Data")
        if kpis:
            kpi_df = pd.DataFrame(list(kpis.items()), columns=["Metric", "Value"])
            kpi_df.to_excel(writer, index=False, sheet_name="KPI Summary")
    return buffer.getvalue()


def to_pdf_summary_bytes(kpis: dict, dept_perf: pd.DataFrame, title: str = "HR Analytics — Management Report") -> bytes:
    """
    Build a lightweight executive-summary PDF using reportlab
    (kept intentionally simple/dependency-light rather than a full
    charting PDF engine).
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(title, styles["Title"]),
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]),
        Spacer(1, 0.5 * cm),
        Paragraph("Executive KPI Summary", styles["Heading2"]),
    ]

    kpi_rows = [["Metric", "Value"]] + [[k.replace("_", " ").title(), str(v)] for k, v in kpis.items()]
    kpi_table = Table(kpi_rows, colWidths=[9 * cm, 6 * cm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6366F1")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.8 * cm))

    story.append(Paragraph("Department Performance", styles["Heading2"]))
    dept_cols = ["department", "avg_rating", "avg_training_score", "kpi_met_pct", "headcount"]
    dept_rows = [["Department", "Avg Rating", "Avg Training Score", "KPI Met %", "Headcount"]]
    for _, r in dept_perf[dept_cols].iterrows():
        dept_rows.append([str(r["department"]), r["avg_rating"], r["avg_training_score"],
                           f"{r['kpi_met_pct']}%", int(r["headcount"])])
    dept_table = Table(dept_rows, colWidths=[4.5 * cm, 2.5 * cm, 3 * cm, 2.5 * cm, 2.5 * cm])
    dept_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#22D3EE")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
    ]))
    story.append(dept_table)

    doc.build(story)
    return buffer.getvalue()
