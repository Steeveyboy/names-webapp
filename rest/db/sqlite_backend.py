"""
SQLite implementation of the DatabaseBackend.

Suitable for local development and single-server deployments.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from db.base import DatabaseBackend
from models import (
    DecadeTrend,
    Gender,
    GenderBreakdown,
    NameByStateRecord,
    NameRecord,
    NameSearchResult,
    NameStats,
    RankedName,
    StateCount,
    YearCount,
)


class SQLiteBackend(DatabaseBackend):
    """SQLite-backed implementation using the stdlib ``sqlite3`` module."""

    def __init__(self, db_path: str = "names_database.db") -> None:
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row  # dict-like access

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._conn

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetchall(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        cur = self.conn.execute(query, params)
        return cur.fetchall()

    def _fetchone(self, query: str, params: tuple = ()):
        cur = self.conn.execute(query, params)
        return cur.fetchone()

    # ------------------------------------------------------------------
    # Core queries — national data
    # ------------------------------------------------------------------

    def get_name_records(self, name: str) -> list[NameRecord]:
        rows = self._fetchall(
            "SELECT name, gender, count, year FROM ssa_names WHERE name = ?",
            (name,),
        )
        return [NameRecord(name=r["name"], gender=r["gender"], count=r["count"], year=r["year"]) for r in rows]

    def get_name_trends(self, name: str, gender: Optional[str] = None) -> list[YearCount]:
        if gender:
            rows = self._fetchall(
                """
                SELECT year, SUM(count) AS count
                FROM ssa_names
                WHERE name = ? AND gender = ?
                GROUP BY year ORDER BY year
                """,
                (name, gender),
            )
        else:
            rows = self._fetchall(
                """
                SELECT year, SUM(count) AS count
                FROM ssa_names
                WHERE name = ?
                GROUP BY year ORDER BY year
                """,
                (name,),
            )
        return [YearCount(year=r["year"], count=r["count"]) for r in rows]

    def get_name_stats(self, name: str) -> Optional[NameStats]:
        summary = self._fetchone(
            """
            SELECT
                SUM(count)                    AS total_count,
                MAX(count)                    AS peak_count,
                MIN(year)                     AS first_year,
                MAX(year)                     AS last_year
            FROM ssa_names
            WHERE name = ?
            """,
            (name,),
        )
        if summary is None or summary["total_count"] is None:
            return None

        # Peak year (year with highest single count)
        peak = self._fetchone(
            """
            SELECT year FROM ssa_names
            WHERE name = ?
            ORDER BY count DESC LIMIT 1
            """,
            (name,),
        )

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
            WHERE name = ?
            GROUP BY gender
            """,
            (name,),
        )
        return [GenderBreakdown(gender=r["gender"], total_count=r["total_count"]) for r in rows]

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
                WHERE year = ? AND gender = ?
                ORDER BY count DESC
                LIMIT ?
                """,
                (year, gender, limit),
            )
        else:
            rows = self._fetchall(
                """
                SELECT name, gender, count,
                       ROW_NUMBER() OVER (ORDER BY count DESC) AS rank
                FROM ssa_names
                WHERE year = ?
                ORDER BY count DESC
                LIMIT ?
                """,
                (year, limit),
            )
        return [RankedName(name=r["name"], gender=r["gender"], count=r["count"], rank=r["rank"]) for r in rows]

    def get_name_rank(self, name: str, year: int, gender: str) -> Optional[int]:
        row = self._fetchone(
            """
            SELECT rank FROM (
                SELECT name,
                       ROW_NUMBER() OVER (ORDER BY count DESC) AS rank
                FROM ssa_names
                WHERE year = ? AND gender = ?
            ) ranked
            WHERE name = ?
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
                WHERE name = ? AND gender = ?
                GROUP BY decade ORDER BY decade
                """,
                (name, gender),
            )
        else:
            rows = self._fetchall(
                """
                SELECT (year / 10) * 10 AS decade, SUM(count) AS count
                FROM ssa_names
                WHERE name = ?
                GROUP BY decade ORDER BY decade
                """,
                (name,),
            )
        return [DecadeTrend(decade=r["decade"], count=r["count"]) for r in rows]

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
                WHERE name = ? AND state = ?
                """,
                (name, state),
            )
        else:
            rows = self._fetchall(
                """
                SELECT state, name, gender, count, year
                FROM ssa_names_by_state
                WHERE name = ?
                """,
                (name,),
            )
        return [
            NameByStateRecord(state=r["state"], name=r["name"], gender=r["gender"], count=r["count"], year=r["year"])
            for r in rows
        ]

    def get_state_distribution(self, name: str) -> list[StateCount]:
        rows = self._fetchall(
            """
            SELECT state, SUM(count) AS count
            FROM ssa_names_by_state
            WHERE name = ?
            GROUP BY state
            ORDER BY count DESC
            """,
            (name,),
        )
        return [StateCount(state=r["state"], count=r["count"]) for r in rows]

    # ------------------------------------------------------------------
    # Search / autocomplete
    # ------------------------------------------------------------------

    def search_names(self, prefix: str, limit: int = 20) -> list[NameSearchResult]:
        rows = self._fetchall(
            """
            SELECT name, SUM(count) AS total_count
            FROM ssa_names
            WHERE name LIKE ? || '%'
            GROUP BY name
            ORDER BY total_count DESC
            LIMIT ?
            """,
            (prefix, limit),
        )
        return [NameSearchResult(name=r["name"], total_count=r["total_count"]) for r in rows]

    # ------------------------------------------------------------------
    # Unique / diversity metrics
    # ------------------------------------------------------------------

    def get_unique_name_count(self, year: Optional[int] = None) -> int:
        if year:
            row = self._fetchone(
                "SELECT COUNT(DISTINCT name) AS cnt FROM ssa_names WHERE year = ?",
                (year,),
            )
        else:
            row = self._fetchone("SELECT COUNT(DISTINCT name) AS cnt FROM ssa_names")
        return row["cnt"] if row else 0

    # ------------------------------------------------------------------
    # Data ingestion
    # ------------------------------------------------------------------

    def init_schema(self, sql_script: str) -> None:
        self.conn.executescript(sql_script)
        self.conn.commit()

    def insert_names_batch(self, records: list[tuple]) -> None:
        self.conn.executemany(
            "INSERT INTO ssa_names (name, gender, count, year) VALUES (?, ?, ?, ?)",
            records,
        )
        self.conn.commit()

    def insert_state_names_batch(self, records: list[tuple]) -> None:
        self.conn.executemany(
            "INSERT INTO ssa_names_by_state (state, name, gender, count, year) VALUES (?, ?, ?, ?, ?)",
            records,
        )
        self.conn.commit()

    def create_indexes(self, table_name: str = "ssa_names") -> None:
        indexes = [
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_name ON {table_name}(name);",
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_year ON {table_name}(year);",
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_name_year ON {table_name}(name, year);",
        ]
        for sql in indexes:
            self.conn.execute(sql)
        self.conn.commit()

    def table_row_count(self, table_name: str) -> int:
        row = self._fetchone(f"SELECT COUNT(*) AS cnt FROM {table_name}")
        return row["cnt"] if row else 0

    def distinct_year_count(self, table_name: str) -> int:
        row = self._fetchone(f"SELECT COUNT(DISTINCT year) AS cnt FROM {table_name}")
        return row["cnt"] if row else 0

    def sample_rows(self, table_name: str, limit: int = 5) -> list[tuple]:
        cur = self.conn.execute(f"SELECT * FROM {table_name} LIMIT ?", (limit,))
        return cur.fetchall()
