# Nomi — Names Analytics Webapp

A full-stack web application for visualizing and analyzing newborn names data from the Social Security Administration (SSA). Explore naming trends, popularity changes, and demographic patterns from 1880 to 2021.

## 🏗️ Project Structure

```
names-webapp/
├── rest/                          # Python FastAPI backend
│   ├── app.py                    # FastAPI application (routes, /docs, /redoc)
│   ├── config.py                 # Env config (DB_BACKEND, SQLITE_DB_PATH)
│   ├── models.py                 # Pydantic v2 contracts
│   ├── db/                       # Pluggable DB backends (SQLite / Postgres)
│   └── names_database.db         # SQLite database (created via ingestion)
├── web/name-analyzer-frontend/   # React 19 + TypeScript + Vite SPA
├── api/index.py                  # Vercel serverless entry (re-exports FastAPI app)
├── data/                         # Ingestion scripts + SQL DDL
│   ├── data_ingestion.py
│   ├── initdb.sql / initdb_postgres.sql
│   └── fetch_data.bash
├── vercel.json                   # Deployment config
├── requirements.txt              # Backend production dependencies
├── requirements-dev.txt          # + Jupyter, seaborn
└── query_maker.ipynb             # Data exploration notebook
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12
- Node.js 18+
- Git

### Clone

```bash
git clone <your-repo-url>
cd names-webapp
```

## 🐍 Backend Setup (FastAPI)

### 1. Create Virtual Environment

```bash
python3.12 -m venv .venv

# Activate:
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt

# For development (includes Jupyter, seaborn)
pip install -r requirements-dev.txt
```

### 3. Populate Database

```bash
cd data
python data_ingestion.py -d

# Move the resulting SQLite DB into rest/
cd ..
mv names_database.db rest/
```

### 4. Verify Database

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('rest/names_database.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM ssa_names')
print(f'Database contains {cursor.fetchone()[0]} records')
conn.close()
"
```

### 5. Run Backend Server

```bash
cd rest
uvicorn app:app --reload
# Production (no auto-reload):
# uvicorn app:app --host 0.0.0.0 --port 8000
```

The API is available at `http://localhost:8000`.

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Using Postgres/Neon instead of SQLite

Set env vars (e.g. in a `.env` file at the project root, loaded automatically by `rest/config.py`):

```bash
DB_BACKEND=postgres
DATABASE_URL=postgresql://<user>:<password>@<host>/<db>?sslmode=require
```

`DB_BACKEND` accepts `sqlite` (default), or `postgres`/`postgresql`/`neon`.

### Test API Endpoints

```bash
curl http://localhost:8000/api/names/John
curl http://localhost:8000/api/names/John/trends
curl "http://localhost:8000/api/rankings/2020?gender=F&limit=5"
```

See `/docs` for the full endpoint catalog: name lookup/trends/stats/gender/decades, year rankings, state-level distribution, prefix search, and diversity metrics.

## 🌐 Frontend Setup

The frontend lives in `web/name-analyzer-frontend/` — React 19 + TypeScript + Vite, Tailwind CSS, Radix UI primitives, and Recharts for charts.

```bash
cd web/name-analyzer-frontend
npm install
npm run dev      # Vite dev server at http://localhost:5173
```

> The dev server has **no proxy** — the FastAPI backend must also be running on `:8000` (App.tsx currently hardcodes `http://localhost:8000`).

Other scripts:

```bash
npm run build    # Production build → dist/
npm run lint     # ESLint
npm run preview  # Preview the production build
```

## 🛠️ Development Workflow

### Backend Development

1. **Run with auto-reload:**
   ```bash
   cd rest
   uvicorn app:app --reload
   ```

2. **Data exploration:**
   ```bash
   jupyter lab query_maker.ipynb
   ```

3. **Database queries:** all DB access goes through the `DatabaseBackend` abstraction in `rest/db/`. Declare new queries on `rest/db/base.py` first, then implement them in both `sqlite_backend.py` and `postgres_backend.py`. See `rest/db/factory.py` for backend selection.

### Frontend Development

Run `npm run dev` from `web/name-analyzer-frontend/` for hot-reload during development. Year-range/state/gender filtering currently happens client-side in `App.tsx`; new features should prefer the versioned `/api/...` endpoints over the legacy `/searchName/<name>` route.

## 📊 Available Data & Analytics

```sql
CREATE TABLE ssa_names(
    name TEXT,      -- First name
    gender CHAR,    -- 'M' or 'F'
    count INTEGER,  -- Number of babies with this name
    year INTEGER    -- Year (1880-2021)
);

CREATE TABLE ssa_names_by_state(
    state TEXT,     -- Two-letter state code
    name TEXT,
    gender CHAR,
    count INTEGER,
    year INTEGER
);
```

### Analytics Features

- **Trend Analysis**: Name popularity over time
- **Gender Distribution**: Male vs Female usage
- **Decade Comparisons**: Popular names by decade
- **Name Rankings**: Top names by year, and a name's rank in a given year
- **State-Level Data**: Distribution of a name across states
- **Search & Discovery**: Prefix search/autocomplete
- **Diversity Metrics**: Count of distinct names, optionally by year

## 🚀 Deployment

Deployed via **Vercel** (`vercel.json`):

- Builds the frontend: `cd web/name-analyzer-frontend && npm install && npm run build`
- Serves the build output from `web/name-analyzer-frontend/dist`
- Routes `/api/*` to `api/index.py`, which adds `rest/` to `sys.path` and re-exports the FastAPI `app`
- Everything else falls back to `index.html` (SPA routing)

Set `DB_BACKEND` and `DATABASE_URL` as Vercel project environment variables to use Postgres/Neon in production.

## 🐛 Troubleshooting

### Common Issues

1. **Database not found**: Ensure `names_database.db` exists in `rest/` (or that `DB_BACKEND=postgres` and `DATABASE_URL` are set correctly).
2. **Import errors**: Activate the virtual environment and reinstall requirements.
3. **CORS errors**: `app.py` enables CORS for all origins by default via `CORSMiddleware`; check the frontend's request URL if you still see errors.
4. **Port conflicts**: Run uvicorn on a different port with `--port <port>`, and update the hardcoded API URL in `App.tsx` to match.
5. **Frontend can't reach backend**: Confirm both servers are running — there is no dev proxy, so `:8000` (API) and `:5173` (Vite) must both be up.

### Development Tips

- Check browser developer tools for frontend errors
- Test API endpoints with `/docs` (Swagger UI), curl, or Postman
- Use a SQLite browser to inspect `rest/names_database.db`

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

[Add your license here]

---

**Happy Hacking! 🎯**
