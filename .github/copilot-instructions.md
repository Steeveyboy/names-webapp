# Copilot Instructions

## Project Overview

**Nomi** is a full-stack baby names analytics app built on SSA data (1880–2021). It has two independent sub-projects:

- **`rest/`** — Python **FastAPI** REST API (backend)
- **`web/name-analyzer-frontend/`** — React 19 + TypeScript + Vite (frontend)

## Commands

### Backend
```bash
# Run the FastAPI dev server (from rest/)
cd rest && uvicorn app:app --reload
# Swagger UI: http://localhost:8000/docs
# ReDoc:      http://localhost:8000/redoc
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

The FastAPI app (`app.py`) never touches the database directly. All queries go through a `DatabaseBackend` interface:

```
app.py  →  db/factory.py  →  db/base.py (ABC)
                           ├── db/sqlite_backend.py   (default)
                           └── db/postgres_backend.py
```

- `db/base.py` defines the abstract `DatabaseBackend` — **all new query methods must be added here first**, then implemented in each backend.
- `db/factory.py` selects the backend based on the `DB_BACKEND` env var (`"sqlite"` by default; `"postgres"` or `"neon"` for Postgres).
- `models.py` contains Pydantic v2 models that form the contract between the DB layer and the API. All routes serialize via `.model_dump()`.
- `config.py` reads env vars (`DB_BACKEND`, `SQLITE_DB_PATH`).
- **Postgres backend** uses `DATABASE_URL` env var for the connection string (DSN). Set this in `.env` for local Postgres/Neon development.
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

The app currently calls the legacy endpoint (`/searchName/<name>` on `http://localhost:8000`, hardcoded in `App.tsx`) and does **client-side filtering** of results (year range, state, gender) in `App.tsx`. New features should prefer the versioned `/api/` endpoints.

## Key Conventions

- **Name normalization happens in `app.py`** — `normalize_name()` calls `.strip().capitalize()` before every DB query. Backends receive already-normalized names and use direct `name = ?` equality (no `LOWER()` needed). SSA data is stored Title Case (e.g. `Mary`, `James`).
- **Gender values are always `"M"` or `"F"`** — use the `Gender` enum from `models.py`.
- **New API routes** follow the pattern: route handler in `app.py` → method on `DatabaseBackend` ABC → implementation in both `sqlite_backend.py` and `postgres_backend.py`.
- **Postgres backend** resolves its DSN from the `DATABASE_URL` env var inside the class.
- The frontend dev server proxying is **not configured** — the frontend calls the FastAPI server directly, so both servers must be running during development (FastAPI on `:8000`, Vite on `:5173`).
