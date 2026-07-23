"""
Database layer for the HR Analytics Platform.

Supports two engines, selected via DB_ENGINE in .env:
  - "sqlite" (default): zero-config, self-creating file database. This is
    what makes `streamlit run app.py` work immediately on a fresh clone
    with no external services.
  - "mysql": production-style engine. Requires MYSQL_* variables in .env.

Either way, the module is fully self-initializing:
  - creates the database if it doesn't exist (MySQL) / creates the file (SQLite)
  - creates the `employees` table if missing, with indexes
  - loads data/processed/employees_clean.csv into it, skipping duplicates,
    the first time it runs (or whenever the table is empty)

No manual SQL needs to be run by the user.
"""
from __future__ import annotations

import logging

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from utils.config import DB, PATHS

logger = logging.getLogger(__name__)

_ENGINE: Engine | None = None

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY,
    department VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    education VARCHAR(100) NOT NULL,
    gender CHAR(1) NOT NULL,
    recruitment_channel VARCHAR(100) NOT NULL,
    no_of_trainings INTEGER NOT NULL,
    age INTEGER NOT NULL,
    previous_year_rating INTEGER,
    length_of_service INTEGER NOT NULL,
    KPIs_met_more_than_80 INTEGER NOT NULL,
    awards_won INTEGER NOT NULL,
    avg_training_score INTEGER NOT NULL
)
"""

INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_department ON employees(department)",
    "CREATE INDEX IF NOT EXISTS idx_region ON employees(region)",
    "CREATE INDEX IF NOT EXISTS idx_gender ON employees(gender)",
]


def _build_engine() -> Engine:
    if DB.engine == "mysql":
        # Create the database itself first (mysql connector, no db selected yet)
        root_url = (
            f"mysql+mysqlconnector://{DB.mysql_user}:{DB.mysql_password}"
            f"@{DB.mysql_host}:{DB.mysql_port}"
        )
        try:
            root_engine = create_engine(root_url)
            with root_engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB.mysql_database}"))
                conn.commit()
        except Exception:
            logger.exception(
                "Could not reach MySQL at %s. Falling back to SQLite. "
                "Check MYSQL_* values in .env if you intended to use MySQL.",
                DB.mysql_host,
            )
            return _build_sqlite_engine()

        url = (
            f"mysql+mysqlconnector://{DB.mysql_user}:{DB.mysql_password}"
            f"@{DB.mysql_host}:{DB.mysql_port}/{DB.mysql_database}"
        )
        return create_engine(url, pool_pre_ping=True)

    return _build_sqlite_engine()


def _build_sqlite_engine() -> Engine:
    PATHS.sqlite_db.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{PATHS.sqlite_db}")


def get_engine() -> Engine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = _build_engine()
    return _ENGINE


def init_db() -> None:
    """Create table + indexes if missing. Idempotent."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(CREATE_TABLE_SQL))
        for stmt in INDEXES_SQL:
            conn.execute(text(stmt))


def table_row_count() -> int:
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM employees"))
        return result.scalar_one()


def seed_from_csv(csv_path=None, force: bool = False) -> int:
    """
    Load the processed CSV into the employees table.
    Skips rows whose employee_id already exists (no duplicate insertion).
    Returns the number of rows inserted.
    """
    csv_path = csv_path or PATHS.processed_csv
    init_db()

    if not force and table_row_count() > 0:
        logger.info("employees table already populated, skipping seed.")
        return 0

    df = pd.read_csv(csv_path)
    engine = get_engine()

    existing_ids: set[int] = set()
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT employee_id FROM employees")).fetchall()
        existing_ids = {r[0] for r in rows}

    new_rows = df[~df["employee_id"].isin(existing_ids)]
    if new_rows.empty:
        return 0

    new_rows.to_sql("employees", engine, if_exists="append", index=False)
    logger.info("Inserted %d new rows into employees.", len(new_rows))
    return len(new_rows)


def ensure_ready() -> pd.DataFrame:
    """
    One-call bootstrap used by the Streamlit app:
    ensure DB + table exist, ensure it's seeded, return the full DataFrame.
    If the processed CSV doesn't exist yet, run the cleaning pipeline first.
    """
    from src.data_cleaning import run_pipeline  # local import avoids cycles

    if not PATHS.processed_csv.exists():
        run_pipeline(PATHS.raw_csv, PATHS.processed_csv)

    init_db()
    if table_row_count() == 0:
        seed_from_csv()

    return fetch_all()


def fetch_all() -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql("SELECT * FROM employees", engine)
