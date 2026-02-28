"""
Data ingestion script for the names web application.

Extracts CSV files from ZIP archives and loads them into the configured
database backend (SQLite for local dev, PostgreSQL/Neon for production).

Usage:
    python data_ingestion.py                 # ingest only
    python data_ingestion.py --download      # download ZIPs first, then ingest
    DB_BACKEND=postgres python data_ingestion.py   # target Neon/Postgres
"""

import sys
import os
import zipfile
import csv
from pathlib import Path
import logging
import argparse
import re

# ---------------------------------------------------------------------------
# Allow imports from the sibling ``rest/`` package so we can reuse the
# database backends and models that live there.
# ---------------------------------------------------------------------------
REST_DIR = Path(__file__).resolve().parent.parent / "rest"
sys.path.insert(0, str(REST_DIR))

from db.factory import create_backend          # noqa: E402
from db.base import DatabaseBackend            # noqa: E402

# ---------------------------------------------------------------------------
# Logging & CLI
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description="Ingest SSA baby-name CSVs into the configured database backend.",
)
parser.add_argument(
    "--download", action="store_true",
    help="Download the ZIP files from ssa.gov before ingestion.",
)
args = parser.parse_args()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
NAMES_ZIP = "names.zip"
NAMES_BY_STATE_ZIP = "namesbystate.zip"


class NamesDataPipeline:
    """
    ETL pipeline that reads SSA CSV archives and loads them via a
    :class:`DatabaseBackend`, so the same script works against SQLite
    *or* PostgreSQL/Neon without code changes.
    """

    def __init__(self, backend: DatabaseBackend) -> None:
        self.db = backend
        self.zip_path = Path(NAMES_ZIP)
        self.names_by_state_zip_path = Path(NAMES_BY_STATE_ZIP)

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def init_database(self) -> None:
        """Read the appropriate SQL schema file and execute it."""
        logger.info("Initializing database schema...")

        # Pick the right DDL for the active backend
        import config  # available because REST_DIR is on sys.path

        if config.DB_BACKEND in ("postgres", "postgresql", "neon"):
            schema_file = "initdb_postgres.sql"
        else:
            schema_file = "initdb.sql"

        try:
            with open(schema_file, "r") as fh:
                sql_script = fh.read()
        except (FileNotFoundError, IOError) as exc:
            logger.error(
                "Could not open '%s' for reading. Expected at: %s",
                schema_file,
                Path(schema_file).resolve(),
            )
            raise exc

        self.db.init_schema(sql_script)
        logger.info("Database schema initialized successfully.")

    # ------------------------------------------------------------------
    # National names
    # ------------------------------------------------------------------

    def extract_and_load(self) -> None:
        """Extract CSVs from the national names ZIP and bulk-insert."""
        logger.info("Opening zip file: %s", self.zip_path)

        total_records = 0
        files_processed = 0

        with zipfile.ZipFile(self.zip_path, "r") as zf:
            csv_files = [
                f for f in zf.namelist()
                if f.endswith(".txt") or f.endswith(".csv")
            ]
            logger.info("Found %d data files in zip archive.", len(csv_files))

            for filename in csv_files:
                year = self._extract_year_from_filename(filename)
                if year is None:
                    logger.warning("Skipping file %s: could not extract year", filename)
                    continue

                logger.info("Processing %s (Year: %d)", filename, year)

                with zf.open(filename) as csv_file:
                    csv_text = csv_file.read().decode("utf-8").splitlines()
                    reader = csv.reader(csv_text)

                    records = [
                        (name, gender, int(count), year)
                        for name, gender, count, *_ in reader
                        if len([name, gender, count]) == 3
                    ]

                self.db.insert_names_batch(records)
                total_records += len(records)
                files_processed += 1
                logger.info("  Inserted %d records from %s", len(records), filename)

        logger.info(
            "National data ingestion complete — %d files, %d records.",
            files_processed,
            total_records,
        )

    # ------------------------------------------------------------------
    # State-level names
    # ------------------------------------------------------------------

    def extract_and_load_states(self) -> None:
        """Extract CSVs from the state-level ZIP and bulk-insert."""
        logger.info("Opening zip file: %s", self.names_by_state_zip_path)

        total_records = 0
        files_processed = 0

        with zipfile.ZipFile(self.names_by_state_zip_path, "r") as zf:
            csv_files = [
                f for f in zf.namelist()
                if f.lower().endswith(".txt") or f.lower().endswith(".csv")
            ]
            logger.info("Found %d data files in zip archive.", len(csv_files))

            for filename in csv_files:
                logger.info("Processing %s", filename)

                with zf.open(filename) as csv_file:
                    csv_text = csv_file.read().decode("utf-8").splitlines()
                    reader = csv.reader(csv_text)

                    records = []
                    for row in reader:
                        if len(row) == 5:
                            state, gender, year, name, count = row
                            records.append((state, name, gender, int(count), int(year)))

                self.db.insert_state_names_batch(records)
                total_records += len(records)
                files_processed += 1
                logger.info("  Inserted %d records from %s", len(records), filename)

        logger.info(
            "State data ingestion complete — %d files, %d records.",
            files_processed,
            total_records,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_year_from_filename(filename: str) -> int | None:
        """Extract a 4-digit year from *filename* (e.g. ``yob1880.txt``)."""
        match = re.search(r"(\d{4})", filename)
        return int(match.group(1)) if match else None

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def verify_data(self, table_name: str = "ssa_names") -> None:
        """Log basic sanity-check numbers for *table_name*."""
        logger.info("Verifying data in '%s'...", table_name)

        total = self.db.table_row_count(table_name)
        logger.info("  Total records : %s", f"{total:,}")

        years = self.db.distinct_year_count(table_name)
        logger.info("  Years covered : %d", years)

        samples = self.db.sample_rows(table_name, limit=5)
        logger.info("  Sample records:")
        for row in samples:
            logger.info("    %s", row)

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Execute the full pipeline: schema → national → state → indexes."""
        try:
            self.init_database()

            self.extract_and_load()
            self.db.create_indexes(table_name="ssa_names")
            self.verify_data(table_name="ssa_names")

            self.extract_and_load_states()
            self.db.create_indexes(table_name="ssa_names_by_state")
            self.verify_data(table_name="ssa_names_by_state")
        except Exception:
            logger.error("Pipeline failed!", exc_info=True)
            raise
        finally:
            self.db.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    backend = create_backend()
    pipeline = NamesDataPipeline(backend)
    pipeline.run()

