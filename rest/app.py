"""
FastAPI REST API for the SSA baby-names analytics application.

The database backend (SQLite or Postgres/Neon) is selected at startup via
the DB_BACKEND environment variable — see config.py.

Swagger UI:  /docs
ReDoc:       /redoc
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from db.factory import create_backend
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


# ── App setup ─────────────────────────────────────────────────────────────

db = create_backend()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    db.close()


app = FastAPI(
    title="Nomi — Baby Names API",
    description="Analytics API for SSA baby-names data (1880–2021).",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ── Health ────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


# ── Name lookup & trends ─────────────────────────────────────────────────

@app.get("/api/names/{name}", response_model=list[NameRecord], tags=["Names"])
def get_name_records(name: str):
    """Raw records for a name (one row per gender per year)."""
    return db.get_name_records(name)


@app.get("/api/names/{name}/trends", response_model=list[YearCount], tags=["Names"])
def get_name_trends(name: str, gender: Optional[str] = Query(None, description="Filter by gender: M or F")):
    """Yearly total counts for a name, optionally filtered by gender."""
    return db.get_name_trends(name, gender=gender)


@app.get("/api/names/{name}/stats", response_model=NameStats, tags=["Names"])
def get_name_stats(name: str):
    """Aggregate statistics for a name: totals, peak year, gender breakdown."""
    stats = db.get_name_stats(name)
    if stats is None:
        raise HTTPException(status_code=404, detail="Name not found")
    return stats


@app.get("/api/names/{name}/gender", response_model=list[GenderBreakdown], tags=["Names"])
def get_gender_breakdown(name: str):
    """Total count for a name split by gender."""
    return db.get_gender_breakdown(name)


@app.get("/api/names/{name}/decades", response_model=list[DecadeTrend], tags=["Names"])
def get_decade_trends(name: str, gender: Optional[str] = Query(None, description="Filter by gender: M or F")):
    """Decade-aggregated counts for a name, optionally filtered by gender."""
    return db.get_decade_trends(name, gender=gender)


# ── Rankings ──────────────────────────────────────────────────────────────

@app.get("/api/rankings/{year}", response_model=list[RankedName], tags=["Rankings"])
def get_top_names(
    year: int,
    gender: Optional[str] = Query(None, description="Filter by gender: M or F"),
    limit: int = Query(10, ge=1, le=1000),
):
    """Top names for a given year, optionally filtered by gender."""
    return db.get_top_names(year, gender=gender, limit=limit)


@app.get("/api/rankings/{year}/{name}", tags=["Rankings"])
def get_name_rank(
    year: int,
    name: str,
    gender: str = Query(..., description="Required: M or F"),
):
    """Rank of a name in a given year for a specific gender."""
    rank = db.get_name_rank(name, year, gender)
    if rank is None:
        raise HTTPException(status_code=404, detail="Name not ranked in that year")
    return {"name": name, "year": year, "gender": gender, "rank": rank}


# ── State-level data ─────────────────────────────────────────────────────

@app.get("/api/names/{name}/states", response_model=list[NameByStateRecord], tags=["States"])
def get_name_by_state(name: str, state: Optional[str] = Query(None, description="Two-letter state code, e.g. CA")):
    """State-level records for a name, optionally filtered to a single state."""
    return db.get_name_by_state(name, state=state)


@app.get("/api/names/{name}/state-distribution", response_model=list[StateCount], tags=["States"])
def get_state_distribution(name: str):
    """Total count per state for a name, ordered descending (useful for choropleth maps)."""
    return db.get_state_distribution(name)


# ── Search / autocomplete ─────────────────────────────────────────────────

@app.get("/api/search", response_model=list[NameSearchResult], tags=["Search"])
def search_names(
    q: str = Query(..., min_length=1, description="Name prefix to search"),
    limit: int = Query(20, ge=1, le=100),
):
    """Prefix search for names, ordered by total popularity. Used for autocomplete."""
    return db.search_names(q, limit=limit)


# ── Diversity metrics ─────────────────────────────────────────────────────

@app.get("/api/diversity", tags=["Diversity"])
def get_unique_name_count(year: Optional[int] = Query(None, description="Restrict count to a specific year")):
    """Number of distinct names in the dataset, optionally filtered by year."""
    count = db.get_unique_name_count(year)
    return {"unique_names": count, "year": year}


# ── Legacy endpoint (backwards compatibility) ─────────────────────────────

@app.get("/searchName/{name}", response_model=list[NameRecord], tags=["Legacy"], deprecated=True)
def search_name_legacy(name: str):
    """Deprecated. Use /api/names/{name} instead."""
    return db.get_name_records(name)


