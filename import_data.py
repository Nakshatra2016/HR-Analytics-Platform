"""
Standalone CLI entry point to (re)build the dataset and database outside
of Streamlit — useful for CI, cron jobs, or a first manual run.

Usage:
    python import_data.py            # clean + seed if not already seeded
    python import_data.py --force    # re-seed even if table has data
"""
from __future__ import annotations

import argparse
import logging

from src.data_cleaning import run_pipeline
from src.database import init_db, seed_from_csv, table_row_count
from utils.config import PATHS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Clean data and (re)seed the HR Analytics database.")
    parser.add_argument("--force", action="store_true", help="Re-seed even if the table already has rows.")
    args = parser.parse_args()

    logger.info("Running cleaning pipeline: %s -> %s", PATHS.raw_csv, PATHS.processed_csv)
    df = run_pipeline(PATHS.raw_csv, PATHS.processed_csv)
    logger.info("Cleaned dataset has %d rows.", len(df))

    init_db()
    inserted = seed_from_csv(force=args.force)
    logger.info("Inserted %d new rows. Table now has %d rows total.", inserted, table_row_count())


if __name__ == "__main__":
    main()
