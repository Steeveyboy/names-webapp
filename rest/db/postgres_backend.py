"""
PostgreSQL / Neon implementation of the DatabaseBackend.

Connects via a connection string sourced **exclusively** from the
``DATABASE_URL`` environment variable (or a ``.env`` file for local
development).  This keeps secrets out of source control.

Uses ``psycopg2`` for the database driver.
"""

from __future__ import annotations

import os
from typing import Any, Optional

import psycopg2  # type: ignore[import-untyped]
import psycopg2.extras  # type: ignore[import-untyped]

from db.base import DatabaseBackend
from models import (
    DecadeTrend,
    GenderBreakdown,
    NameByStateRecord,
    NameRecord,
    NameSearchResult,
    NameStats,
    RankedName,
    StateCount,
    YearCount,
)


def _get_connection_string() -> str:
    """
    Resolve the Postgres connection string securely.

    Resolution order:
      1. ``DATABASE_URL`` environment variable (always wins — set in
         production, CI, Docker, etc.)
      2. ``.env`` file in the project root (local development convenience,
         loaded by ``python-dotenv``).

    Raises ``EnvironmentError`` if no connection string is found.
    """
    url = os.environ.get("DATABASE_URL")
    if url:
        return url

    # Attempt to load from .env for local development
    try:
        from dotenv import load_dotenv

        load_dotenv()
        url = os.environ.get("DATABASE_URL")
    except ImportError:
        pass

    if not url:
        raise EnvironmentError(
            "DATABASE_URL is not set.  Provide it as an environment variable "
            "or in a .env file at the project root."
        )
    return url


class PostgresBackend(DatabaseBackend):
    """
    PostgreSQL / Neon–hosted implementation.

    All queries use parameterised statements (``%s`` placeholders) to
    prevent SQL injection.  ``RealDictCursor`` is used so rows behave
    like dictionaries.
    """

    def __init__(self, dsn: Optional[str] = None) -> None:
        """
        Args:
            dsn: Optional explicit connection string.  If omitted the
                 string is resolved from the environment (recommended).
        """
        self._dsn = dsn or _get_connection_string()
        self._conn = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        self._conn = psycopg2.connect(self._dsn, cursor_factory=psycopg2.extras.RealDictCursor)

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    @property
    def conn(self):
        if self._conn is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._conn

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetchall(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()  # type: ignore[return-value]

    def _fetchone(self, query: str, params: tuple = ()) -> dict[str, Any] | None:
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Core queries — national data
    # ------------------------------------------------------------------

    def get_name_records(self, name: str) -> list[NameRecord]:
        rows = self._fetchall(
            "SELECT name, gender, count, year FROM ssa_names WHERE LOWER(name) = LOWER(%s)",
            (name,),
        )
        return [NameRecord(**r) for r in rows]

    def get_name_trends(self, name: str, gender: Optional[str] = None) -> list[YearCount]:
        if gender:
            rows = self._fetchall(
                """
                SELECT year, SUM(count) AS count
                FROM ssa_names
                WHERE LOWER(name) = LOWER(%s) AND gender = %s
                GROUP BY year ORDER BY year
                """,
                (name, gender),
            )
        else:
            rows = self._fetchall(
                """
                SELECT year, SUM(count) AS count
                FROM ssa_names
                WHERE LOWER(name) = LOWER(%s)
                GROUP BY year ORDER BY year
                """,
                (name,),
            )
        return [YearCount(**r) for r in rows]

    def get_name_stats(self, name: str) -> Optional[NameStats]:
        summary = self._fetchone(
            """
            SELECT
                SUM(count)  AS total_count,
                MAX(count)  AS peak_count,
                MIN(year)   AS first_year,
                MAX(year)   AS last_year
            FROM ssa_names
            WHERE LOWER(name) = LOWER(%s)
            """,
            (name,),
        )
        if summary is None or summary["total_count"] is None:
            return None

        peak = self._fetchone(
            """
            SELECT year FROM ssa_names
            WHERE LOWER(name) = LOWER(%s)
            ORDER BY count DESC LIMIT 1
            """,
            (name,),
        )
        if peak is None:
            return None

        breakdown = self.get_gender_breakdown(name)

        return NameStats(
            name=name,
            total_count=summary["total_count"],
            peak_year=peak["year"],
            peak_count=summary["peak_count"],
            first_year=summary["first_year"],
            last_year=summary["last_year"],
            gender_breakdown=breakdown,
        )

    def get_gender_breakdown(self, name: str) -> list[GenderBreakdown]:
        rows = self._fetchall(
            """
            SELECT gender, SUM(count) AS total_count
            FROM ssa_names
            WHERE LOWER(name) = LOWER(%s)
            GROUP BY gender
            """,
            (name,),
        )
        return [GenderBreakdown(**r) for r in rows]

    # ------------------------------------------------------------------
    # Rankings & popularity
    # ------------------------------------------------------------------

    def get_top_names(
        self,
        year: int,
        gender: Optional[str] = None,
        limit: int = 10,
    ) -> list[RankedName]:
        if gender:
            rows = self._fetchall(
                """
                SELECT name, gender, count,
                       ROW_NUMBER() OVER (ORDER BY count DESC) AS rank
                FROM ssa_names
                WHERE year = %s AND gender = %s
                ORDER BY count DESC
                LIMIT %s
                """,
                (year, gender, limit),
            )
        else:
            rows = self._fetchall(
                """
                SELECT name, gender, count,
                       ROW_NUMBER() OVER (ORDER BY count DESC) AS rank
                FROM ssa_names
                WHERE year = %s
                ORDER BY count DESC
                LIMIT %s
                """,
                (year, limit),
            )
        return [RankedName(**r) for r in rows]

    def get_name_rank(self, name: str, year: int, gender: str) -> Optional[int]:
        row = self._fetchone(
            """
            SELECT rank FROM (
                SELECT name,
                       ROW_NUMBER() OVER (ORDER BY count DESC) AS rank
                FROM ssa_names
                WHERE year = %s AND gender = %s
            ) ranked
            WHERE LOWER(name) = LOWER(%s)
            """,
            (year, gender, name),
        )
        return row["rank"] if row else None

    # ------------------------------------------------------------------
    # Decade / era analysis
    # ------------------------------------------------------------------

    def get_decade_trends(self, name: str, gender: Optional[str] = None) -> list[DecadeTrend]:
        if gender:
            rows = self._fetchall(
                """
                SELECT (year / 10) * 10 AS decade, SUM(count) AS count
                FROM ssa_names
                WHERE LOWER(name) = LOWER(%s) AND gender = %s
                GROUP BY decade ORDER BY decade
                """,
                (name, gender),
            )
        else:
            rows = self._fetchall(
                """
                SELECT (year / 10) * 10 AS decade, SUM(count) AS count
                FROM ssa_names
                WHERE LOWER(name) = LOWER(%s)
                GROUP BY decade ORDER BY decade
                """,
                (name,),
            )
        return [DecadeTrend(**r) for r in rows]

    # ------------------------------------------------------------------
    # State-level data
    # ------------------------------------------------------------------

    def get_name_by_state(
        self,
        name: str,
        state: Optional[str] = None,
    ) -> list[NameByStateRecord]:
        if state:
            rows = self._fetchall(
                """
                SELECT state, name, gender, count, year
                FROM ssa_names_by_state
                WHERE LOWER(name) = LOWER(%s) AND state = %s
                """,
                (name, state),
            )
        else:
            rows = self._fetchall(
                """
                SELECT state, name, gender, count, year
                FROM ssa_names_by_state
                WHERE LOWER(name) = LOWER(%s)
                """,
                (name,),
            )
        return [NameByStateRecord(**r) for r in rows]

    def get_state_distribution(self, name: str) -> list[StateCount]:
        rows = self._fetchall(
            """
            SELECT state, SUM(count) AS count
            FROM ssa_names_by_state
            WHERE LOWER(name) = LOWER(%s)
            GROUP BY state
            ORDER BY count DESC
            """,
            (name,),
        )
        return [StateCount(**r) for r in rows]

    # ------------------------------------------------------------------
    # Search / autocomplete
    # ------------------------------------------------------------------

    def search_names(self, prefix: str, limit: int = 20) -> list[NameSearchResult]:
        rows = self._fetchall(
            """
            SELECT name, SUM(count) AS total_count
            FROM ssa_names
            WHERE LOWER(name) LIKE LOWER(%s || '%%')
            GROUP BY name
            ORDER BY total_count DESC
            LIMIT %s
            """,
            (prefix, limit),
        )
        return [NameSearchResult(**r) for r in rows]

    # ------------------------------------------------------------------
    # Unique / diversity metrics
    # ------------------------------------------------------------------

    def get_unique_name_count(self, year: Optional[int] = None) -> int:
        if year:
            row = self._fetchone(
                "SELECT COUNT(DISTINCT name) AS cnt FROM ssa_names WHERE year = %s",
                (year,),
            )
        else:
            row = self._fetchone("SELECT COUNT(DISTINCT name) AS cnt FROM ssa_names")
        return row["cnt"] if row else 0

    # ------------------------------------------------------------------
    # Data ingestion
    # ------------------------------------------------------------------

    def init_schema(self, sql_script: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute(sql_script)
        self.conn.commit()

    def insert_names_batch(self, records: list[tuple]) -> None:
        with self.conn.cursor() as cur:
            psycopg2.extras.execute_values(
                cur,
                "INSERT INTO ssa_names (name, gender, count, year) VALUES %s",
                records,
                page_size=5000,
            )
        self.conn.commit()

    def insert_state_names_batch(self, records: list[tuple]) -> None:
        with self.conn.cursor() as cur:
            psycopg2.extras.execute_values(
                cur,
                "INSERT INTO ssa_names_by_state (state, name, gender, count, year) VALUES %s",
                records,
                page_size=5000,
            )
        self.conn.commit()

    def create_indexes(self, table_name: str = "ssa_names") -> None:
        with self.conn.cursor() as cur:
            for sql in [
                f"CREATE INDEX IF NOT EXISTS idx_{table_name}_name ON {table_name}(name);",
                f"CREATE INDEX IF NOT EXISTS idx_{table_name}_year ON {table_name}(year);",
                f"CREATE INDEX IF NOT EXISTS idx_{table_name}_name_year ON {table_name}(name, year);",
            ]:
                cur.execute(sql)
        self.conn.commit()

    def table_row_count(self, table_name: str) -> int:
        row = self._fetchone(f"SELECT COUNT(*) AS cnt FROM {table_name}")
        return row["cnt"] if row else 0

    def distinct_year_count(self, table_name: str) -> int:
        row = self._fetchone(f"SELECT COUNT(DISTINCT year) AS cnt FROM {table_name}")
        return row["cnt"] if row else 0

    def sample_rows(self, table_name: str, limit: int = 5) -> list[tuple]:
        rows = self._fetchall(f"SELECT * FROM {table_name} LIMIT %s", (limit,))
        return [tuple(r.values()) for r in rows]
