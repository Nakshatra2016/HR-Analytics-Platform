# 📊 HR Analytics Platform

An end-to-end HR analytics application: a self-initializing database layer,
a reusable Python analytics/query module, and an interactive Plotly +
Streamlit dashboard for exploring employee performance, training,
retention, and diversity.

> Built as a portfolio project demonstrating data engineering, SQL,
> Python architecture, and dashboard/UX design for Data/Business Analyst
> roles.

---

## ✨ Features

- **Zero-config startup** — first run auto-cleans the raw data, creates the
  database, and seeds it. No manual SQL required.
- **Dual database support** — SQLite by default (nothing to install), or
  MySQL for a production-style setup (toggle via `.env`).
- **Duplicate-safe seeding** — re-running the app never double-inserts rows.
- **11 dashboard pages** — Overview, Employee Insights, Performance,
  Training, Department, Retention, Diversity, Raw Data, Downloads, About —
  all driven by one shared filter sidebar.
- **12+ chart types** — bar, pie, treemap, sunburst, heatmap, box, violin,
  scatter, histogram, line, area — all interactive Plotly charts with a
  consistent dark/glassmorphism theme.
- **Exportable reports** — CSV, Excel (multi-sheet with KPI summary), and a
  generated PDF executive summary.
- **Clean architecture** — database, queries, cleaning, charts, and pages
  are separated into single-responsibility modules (see below).

---

## 🏗️ Architecture

```
HR_Analytics_Platform/
├── app.py                    # Streamlit entry point / router
├── import_data.py            # Standalone CLI to clean + seed the DB
├── dashboard/
│   ├── theme.py               # Custom CSS + KPI card templates
│   ├── filters.py             # Sidebar filter widgets
│   └── pages.py               # One render function per dashboard page
├── src/
│   ├── data_cleaning.py       # Raw CSV -> cleaned, typed, deduplicated data
│   ├── database.py            # Engine-agnostic DB init/seed/fetch (SQLite/MySQL)
│   ├── queries.py              # Pure analytics functions (KPIs, groupbys)
│   └── reports.py              # CSV / Excel / PDF report builders
├── utils/
│   ├── config.py               # Paths + env-driven configuration
│   └── charts.py                # Reusable, styled Plotly chart builders
├── database/
│   ├── schema.sql               # Reference MySQL schema (for manual use)
│   └── seed.sql                 # Reference upsert pattern (for manual use)
├── data/
│   ├── raw/employees_raw.csv     # Source data (synthetic sample included)
│   └── processed/                # Auto-generated cleaned CSV (gitignored)
├── notebooks/                    # Exploratory analysis notebook
├── reports/                      # Generated report output (gitignored)
├── images/                       # Dashboard screenshots
├── requirements.txt
├── .env.example
├── Dockerfile
└── LICENSE
```

**Data flow:** `data/raw/employees_raw.csv` → `src/data_cleaning.py`
(dedup, type coercion, missing-value handling) → `data/processed/employees_clean.csv`
→ `src/database.py` (auto-create DB/table/indexes, duplicate-safe insert) →
`src/queries.py` (KPI + groupby functions) → `utils/charts.py` (Plotly figures)
→ `dashboard/pages.py` (rendered in Streamlit).

---

## 📦 A note on the data

No employee CSV shipped with the original project handoff, so this repo
ships a **synthetic dataset** (`data/raw/employees_raw.csv`, ~2,200 rows)
generated to match the exact target schema — including intentional
duplicate IDs and missing ratings, so the cleaning pipeline has something
real to fix. **To use your real data**, replace that file with your own CSV
using the same column names:

```
employee_id, department, region, education, gender, recruitment_channel,
no_of_trainings, age, previous_year_rating, length_of_service,
KPIs_met_more_than_80, awards_won, avg_training_score
```

Delete `data/processed/employees_clean.csv` and `database/hr_analytics.db`
(or run `python import_data.py --force`) to rebuild from the new source.

---

## 🚀 Installation & Running

```bash
git clone <your-repo-url>
cd HR_Analytics_Platform

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

streamlit run app.py
```

That's it — the app cleans the data, creates `database/hr_analytics.db`
(SQLite), and seeds it automatically on first load.

### Using MySQL instead of SQLite

```bash
cp .env.example .env
# edit .env: set DB_ENGINE=mysql and your MYSQL_* credentials
streamlit run app.py
```

The app will create the `hr_analytics` database and `employees` table on
MySQL automatically (equivalent to `database/schema.sql`).

### CLI-only data refresh (no Streamlit)

```bash
python import_data.py           # seed if empty
python import_data.py --force   # re-seed regardless
```

---

## 🐳 Docker

```bash
docker build -t hr-analytics .
docker run -p 8501:8501 hr-analytics
```

Open `http://localhost:8501`.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Dashboard | Streamlit, custom CSS (glassmorphism) |
| Charts | Plotly Express / Graph Objects |
| Data processing | Pandas, NumPy |
| Database | SQLAlchemy — SQLite (default) or MySQL |
| Reports | XlsxWriter, ReportLab |
| Deployment | Docker, Streamlit Community Cloud, Render, Railway |

---

## 🔭 Future Improvements

- Add authentication/role-based views for HR vs. management users
- Add a light theme toggle alongside the current dark theme
- Wire the notebook's model (attrition/promotion prediction) into the dashboard
- Add automated tests (pytest) for `src/data_cleaning.py` and `src/queries.py`
- CI pipeline (GitHub Actions) running lint + tests on push

---

## 👤 Author

**Nakshat Khanna**

## 📄 License

MIT — see [LICENSE](LICENSE).
