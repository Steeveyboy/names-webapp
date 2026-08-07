# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Nomi** — a full-stack baby names analytics app over SSA data (1880–2021). Two independent sub-projects:

- `rest/` — Python **FastAPI** REST API
- `web/name-analyzer-frontend/` — React 19 + TypeScript + Vite SPA
- `api/index.py` — Vercel serverless entry that re-exports the FastAPI `app` from `rest/`
- `data/` — ingestion scripts and SQL DDL (`initdb.sql`, `initdb_postgres.sql`)

## Commands

### Backend (run from `rest/`)
```bash
cd rest && uvicorn app:app --reload   # Swagger UI: /docs, ReDoc: /redoc
```

### Frontend (run from `web/name-analyzer-frontend/`)
```bash
npm run dev      # Vite dev server (:5173)
npm run build    # Production build → dist/
npm run lint     # ESLint
npm run preview  # Preview prod build
```

The frontend dev server has **no proxy** — both servers must run during development (FastAPI on `:8000`, Vite on `:5173`). The API base URL comes from `import.meta.env.VITE_API_URL` (falling back to `''`, i.e. same-origin, which is what production uses). `web/name-analyzer-frontend/.env.development` is checked in and sets it to `http://localhost:8000`.

### First-time data ingestion
```bash
cd data && python data_ingestion.py -d
mv names_database.db ../rest/
```

## Architecture

### Backend: pluggable DB backend

`app.py` never touches the database directly. All queries route through an abstract backend:

```
app.py  →  db/factory.py  →  db/base.py (DatabaseBackend ABC)
                           ├── db/sqlite_backend.py   (default)
                           └── db/postgres_backend.py (Neon)
```

- **Adding a query**: declare the method on `db/base.py` first, then implement in *both* `sqlite_backend.py` and `postgres_backend.py`. Route handler in `app.py` calls it via the `db` singleton from `create_backend()`.
- `db/factory.py` picks backend from `DB_BACKEND` env var (`sqlite` default; `postgres`/`postgresql`/`neon` use the Postgres backend).
- Postgres backend resolves its DSN from `DATABASE_URL` (set in `.env`).
- `models.py` — Pydantic v2 contracts shared between DB layer and API.
- `config.py` — reads env (`DB_BACKEND`, `SQLITE_DB_PATH`), loads `.env` from project root.

### Name normalization (important)

`normalize_name()` in `app.py` calls `.strip().capitalize()` **before every DB query**. SSA data is stored Title Case (`Mary`, `James`), so backends use direct `name = ?` equality — no `LOWER()`, indexes stay usable. Do not duplicate the normalization in the backend layer.

### Gender values

Always `"M"` or `"F"`. Use the `Gender` enum from `models.py`.

### Database schema

```sql
ssa_names(name TEXT, gender CHAR, count INTEGER, year INTEGER)
ssa_names_by_state(state TEXT, name TEXT, gender CHAR, count INTEGER, year INTEGER)
```

### Frontend stack

React 19 + TS + Vite, **Recharts** for charts, **Radix UI** primitives, **Tailwind CSS**, shadcn/ui-style components under `src/components/ui/`.

`App.tsx` fetches from the versioned endpoints — `/api/names/<name>`, or `/api/names/<name>/states?state=<state>` when a state filter is active — then pivots the flat `NameRecord[]` into per-year `{ year, male, female }` rows for the chart. Filtering is split:

- **State** — pushed to the backend (endpoint choice above).
- **Year range and gender** — still applied **client-side** in `handleSearch`. Gender filtering nulls out the unwanted series rather than dropping points, to keep the chart's axis scale stable.

The legacy `/searchName/<name>` endpoint is marked `deprecated=True` in `app.py` and is no longer used by the frontend. New features should use the versioned `/api/...` endpoints (see `app.py` for the full catalog).

### Deployment

`vercel.json` runs the root `npm run build`, which is a thin wrapper that installs and builds the frontend via `--prefix web/name-analyzer-frontend`; the root `package.json` exists purely so Vercel detects the Vite SPA alongside the Python API. Output is served from `web/name-analyzer-frontend/dist`.

Two rewrites: `/api/*` → `api/index.py` (adds `rest/` to `sys.path` and re-exports `app` for the `@vercel/python` runtime), and everything else → `index.html` (SPA fallback). Because `/api/*` is same-origin in production, `VITE_API_URL` should stay unset there.