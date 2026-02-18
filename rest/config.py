"""
Application configuration.

Uses environment variables with sensible defaults for local development.
"""

from __future__ import annotations

import os


# ---------------------------------------------------------------------------
# Database backend selection
# ---------------------------------------------------------------------------
# Set DB_BACKEND to "postgres" (or "neon") to use the PostgreSQL backend.
# Defaults to "sqlite" for zero-setup local development.
DB_BACKEND: str = os.environ.get("DB_BACKEND", "sqlite").lower()

# SQLite-specific
SQLITE_DB_PATH: str = os.environ.get("SQLITE_DB_PATH", "names_database.db")

# Flask
FLASK_DEBUG: bool = os.environ.get("FLASK_DEBUG", "0") == "1"
