"""
Pydantic data models representing SSA baby names data.

These models serve as the contract between the database layer and the API,
ensuring type safety and consistent serialization regardless of backend.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Gender(str, Enum):
    MALE = "M"
    FEMALE = "F"


# ---------------------------------------------------------------------------
# Core database row models
# ---------------------------------------------------------------------------

class NameRecord(BaseModel):
    """Single row from the national `ssa_names` table."""
    name: str
    gender: Gender
    count: int = Field(ge=0)
    year: int = Field(ge=1880)


class NameByStateRecord(BaseModel):
    """Single row from the `ssa_names_by_state` table."""
    state: str = Field(min_length=2, max_length=2)
    name: str
    gender: Gender
    count: int = Field(ge=0)
    year: int = Field(ge=1880)


# ---------------------------------------------------------------------------
# Aggregate / analytics response models
# ---------------------------------------------------------------------------

class YearCount(BaseModel):
    """A single (year, count) data-point — used for trend lines."""
    year: int
    count: int


class GenderBreakdown(BaseModel):
    """Total count for a name split by gender."""
    gender: Gender
    total_count: int


class NameStats(BaseModel):
    """High-level statistics for a given name."""
    name: str
    total_count: int
    peak_year: int
    peak_count: int
    first_year: int
    last_year: int
    gender_breakdown: list[GenderBreakdown]


class RankedName(BaseModel):
    """A name with its rank for a given year/context."""
    name: str
    gender: Gender
    count: int
    rank: int


class DecadeTrend(BaseModel):
    """Aggregated count for a name within a decade."""
    decade: int  # e.g. 1990
    count: int


class StateCount(BaseModel):
    """Aggregate count for a name within a state."""
    state: str
    count: int


class NameSearchResult(BaseModel):
    """Lightweight result returned by autocomplete / prefix search."""
    name: str
    total_count: int
