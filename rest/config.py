"""
Application configuration.

Uses environment variables with sensible defaults for local development.
Loads a ``.env`` file (if present) from the project root for convenience.
"""

from __future__ import annotations

import os

# Load .env before reading any config values
try:
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Database backend selection
# ---------------------------------------------------------------------------
# Set DB_BACKEND to "postgres" (or "neon") to use the PostgreSQL backend.
# Defaults to "sqlite" for zero-setup local development.
DB_BACKEND: str = os.environ.get("DB_BACKEND", "sqlite").lower()

# SQLite-specific
SQLITE_DB_PATH: str = os.environ.get("SQLITE_DB_PATH", "names_database.db")


