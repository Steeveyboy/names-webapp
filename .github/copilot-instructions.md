# Copilot Instructions

## Project Overview

**Nomi** is a full-stack baby names analytics app built on SSA data (1880–2021). It has two independent sub-projects:

- **`rest/`** — Python Flask REST API (backend)
- **`web/name-analyzer-frontend/`** — React 19 + TypeScript + Vite (frontend)

## Commands

### Backend
```bash
# Run the FastAPI dev server (from rest/)
cd rest && uvicorn app:app --reload
# Swagger UI available at http://localhost:8000/docs
```

### Frontend
```bash
cd web/name-analyzer-frontend

npm run dev      # Start Vite dev server
npm run build    # Production build
npm run lint     # ESLint
npm run preview  # Preview production build
```

### Data ingestion (first-time setup)
```bash
cd data && python data_ingestion.py -d
mv names_database.db ../rest/
```

## Architecture

### Backend (`rest/`)

The Flask app (`app.py`) never touches the database directly. All queries go through a `DatabaseBackend` interface:

```
app.py  →  db/factory.py  →  db/base.py (ABC)
                           ├── db/sqlite_backend.py   (default)
                           └── db/postgres_backend.py
```

- `db/base.py` defines the abstract `DatabaseBackend` — **all new query methods must be added here first**, then implemented in each backend.
- `db/factory.py` selects the backend based on the `DB_BACKEND` env var (`"sqlite"` by default; `"postgres"` or `"neon"` for Postgres).
- `models.py` contains Pydantic v2 models that form the contract between the DB layer and the API. All routes serialize via `.model_dump()`.
- `config.py` reads env vars (`DB_BACKEND`, `SQLITE_DB_PATH`, `FLASK_DEBUG`).
- `dbWrapper.py` is a **legacy file** — do not use it for new code.

### Database schema

```sql
-- National data
CREATE TABLE ssa_names (
    name    TEXT,
    gender  CHAR,   -- 'M' or 'F'
    count   INTEGER,
    year    INTEGER
);

-- State-level data
CREATE TABLE ssa_names_by_state (
    state   TEXT,   -- 2-letter code, e.g. 'CA'
    name    TEXT,
    gender  CHAR,
    count   INTEGER,
    year    INTEGER
);
```

### Frontend (`web/name-analyzer-frontend/`)

React 19 + TypeScript SPA using:
- **Recharts** for data visualization
- **Radix UI** for accessible primitives
- **Tailwind CSS** for styling (configured via `tailwind.config.js` / `vite.config.js`)
- **shadcn/ui**-style components in `src/components/ui/`

The app currently calls the legacy endpoint (`/searchName/<name>` on `http://localhost:8000`) and does **client-side filtering** of results (year range, state, gender) in `App.tsx`. New features should prefer the versioned `/api/` endpoints.

## Key Conventions

- **All DB queries are case-insensitive** — use `LOWER(name) = LOWER(?)` or `LOWER(name) LIKE LOWER(? || '%')`.
- **Gender values are always `"M"` or `"F"`** — use the `Gender` enum from `models.py`.
- **New API routes** follow the pattern: route handler in `app.py` → method on `DatabaseBackend` ABC → implementation in both `sqlite_backend.py` and `postgres_backend.py`.
- **Postgres backend** resolves its DSN from an env var inside the class; check `postgres_backend.py` for the expected variable name before adding Postgres-specific features.
- The frontend dev server proxying is **not configured** — the frontend calls the Flask API directly, so both servers must be running during development (Flask on `:5000` or `:8000`, Vite on `:5173`).
