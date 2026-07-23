"""
Central configuration for the HR Analytics Platform.

All environment-dependent values (database engine, credentials, paths) live
here so the rest of the codebase never hardcodes a secret or a path.

Copy `.env.example` to `.env` and edit values as needed. Nothing here
requires manual editing to get a working local run - defaults to a
zero-config SQLite database.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load variables from a .env file if present (does nothing if absent).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Paths:
    root: Path = PROJECT_ROOT
    raw_csv: Path = PROJECT_ROOT / "data" / "raw" / "employees_raw.csv"
    processed_csv: Path = PROJECT_ROOT / "data" / "processed" / "employees_clean.csv"
    sqlite_db: Path = PROJECT_ROOT / "database" / "hr_analytics.db"
    schema_sql: Path = PROJECT_ROOT / "database" / "schema.sql"
    seed_sql: Path = PROJECT_ROOT / "database" / "seed.sql"
    reports_dir: Path = PROJECT_ROOT / "reports"
    images_dir: Path = PROJECT_ROOT / "images"


@dataclass(frozen=True)
class DBConfig:
    # "sqlite" (default, zero-config) or "mysql"
    engine: str = os.getenv("DB_ENGINE", "sqlite").strip().lower()

    mysql_host: str = os.getenv("MYSQL_HOST", "localhost")
    mysql_user: str = os.getenv("MYSQL_USER", "root")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "")
    mysql_database: str = os.getenv("MYSQL_DATABASE", "hr_analytics")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))


PATHS = Paths()
DB = DBConfig()

# App-wide constants
APP_TITLE = "HR Analytics Platform"
APP_ICON = "📊"
CACHE_TTL_SECONDS = 300

KPI_TARGET_COLUMNS = [
    "employee_id", "department", "region", "education", "gender",
    "recruitment_channel", "no_of_trainings", "age", "previous_year_rating",
    "length_of_service", "KPIs_met_more_than_80", "awards_won",
    "avg_training_score",
]
