"""
Abstract base class defining the database contract.

Every backend (SQLite, Postgres/Neon, …) implements this interface so the
REST layer is completely decoupled from the storage engine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

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


class DatabaseBackend(ABC):
    """High-level, storage-agnostic interface for the SSA names database."""

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @abstractmethod
    def connect(self) -> None:
        """Establish a connection to the database."""

    @abstractmethod
    def close(self) -> None:
        """Gracefully close the database connection."""

    # ------------------------------------------------------------------
    # Core queries — national data
    # ------------------------------------------------------------------

    @abstractmethod
    def get_name_records(self, name: str) -> list[NameRecord]:
        """Return every national row for *name*.

        The name is normalised to Title Case before querying so that
        indexes on the ``name`` column can be used directly.
        """

    @abstractmethod
    def get_name_trends(self, name: str, gender: Optional[str] = None) -> list[YearCount]:
        """
        Yearly total counts for *name*, optionally filtered by gender.
        Results are ordered by year ascending.
        """

    @abstractmethod
    def get_name_stats(self, name: str) -> Optional[NameStats]:
        """
        Aggregate statistics for *name*: total count, peak year,
        first/last appearance, and gender breakdown.
        Returns ``None`` if the name does not exist.
        """

    @abstractmethod
    def get_gender_breakdown(self, name: str) -> list[GenderBreakdown]:
        """Total counts for *name* grouped by gender."""

    # ------------------------------------------------------------------
    # Rankings & popularity
    # ------------------------------------------------------------------

    @abstractmethod
    def get_top_names(
        self,
        year: int,
        gender: Optional[str] = None,
        limit: int = 10,
    ) -> list[RankedName]:
        """Top *limit* names for a given *year*, optionally filtered by gender."""

    @abstractmethod
    def get_name_rank(self, name: str, year: int, gender: str) -> Optional[int]:
        """
        Rank of *name* for a specific *year* and *gender*.
        Returns ``None`` if the name was not registered that year.
        """

    # ------------------------------------------------------------------
    # Decade / era analysis
    # ------------------------------------------------------------------

    @abstractmethod
    def get_decade_trends(self, name: str, gender: Optional[str] = None) -> list[DecadeTrend]:
        """Counts aggregated by decade for *name*."""

    # ------------------------------------------------------------------
    # State-level data
    # ------------------------------------------------------------------

    @abstractmethod
    def get_name_by_state(
        self,
        name: str,
        state: Optional[str] = None,
    ) -> list[NameByStateRecord]:
        """
        State-level records for *name*.  Optionally narrow to a single *state*.
        """

    @abstractmethod
    def get_state_distribution(self, name: str) -> list[StateCount]:
        """Total count per state for *name*, ordered descending by count."""

    # ------------------------------------------------------------------
    # Search / autocomplete
    # ------------------------------------------------------------------

    @abstractmethod
    def search_names(self, prefix: str, limit: int = 20) -> list[NameSearchResult]:
        """
        Return names matching *prefix* (case-insensitive), ordered by
        total popularity.  Used for autocomplete.
        """

    # ------------------------------------------------------------------
    # Unique / diversity metrics
    # ------------------------------------------------------------------

    @abstractmethod
    def get_unique_name_count(self, year: Optional[int] = None) -> int:
        """
        Number of distinct names.  If *year* is provided, restrict to that year.
        """

    # ------------------------------------------------------------------
    # Data ingestion (used by the ingestion pipeline)
    # ------------------------------------------------------------------

    @abstractmethod
    def init_schema(self, sql_script: str) -> None:
        """
        Execute a DDL script to (re)create the database tables.

        For SQLite this runs ``executescript``; for Postgres the script is
        executed as a single statement block.
        """

    @abstractmethod
    def insert_names_batch(self, records: list[tuple]) -> None:
        """
        Bulk-insert rows into ``ssa_names``.

        Each tuple: ``(name, gender, count, year)``.
        """

    @abstractmethod
    def insert_state_names_batch(self, records: list[tuple]) -> None:
        """
        Bulk-insert rows into ``ssa_names_by_state``.

        Each tuple: ``(state, name, gender, count, year)``.
        """

    @abstractmethod
    def create_indexes(self, table_name: str = "ssa_names") -> None:
        """Create performance indexes on *table_name*."""

    @abstractmethod
    def table_row_count(self, table_name: str) -> int:
        """Return the number of rows in *table_name*."""

    @abstractmethod
    def distinct_year_count(self, table_name: str) -> int:
        """Return the number of distinct years in *table_name*."""

    @abstractmethod
    def sample_rows(self, table_name: str, limit: int = 5) -> list[tuple]:
        """Return a handful of sample rows for verification."""
