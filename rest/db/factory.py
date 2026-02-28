"""
Factory for creating the appropriate DatabaseBackend based on configuration.
"""

from __future__ import annotations

import config
from db.base import DatabaseBackend


def create_backend() -> DatabaseBackend:
    """
    Instantiate and connect the database backend indicated by ``config.DB_BACKEND``.

    Returns a ready-to-use :class:`DatabaseBackend` instance.
    """
    backend_key = config.DB_BACKEND

    if backend_key in ("postgres", "postgresql", "neon"):
        from db.postgres_backend import PostgresBackend

        backend = PostgresBackend()  # DSN resolved from env inside the class
    elif backend_key == "sqlite":
        from db.sqlite_backend import SQLiteBackend

        backend = SQLiteBackend(db_path=config.SQLITE_DB_PATH)
    else:
        raise ValueError(
            f"Unknown DB_BACKEND '{backend_key}'.  "
            "Supported values: 'sqlite', 'postgres', 'neon'."
        )

    backend.connect()
    return backend
