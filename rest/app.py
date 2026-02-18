"""
Flask REST API for the SSA baby-names analytics application.

The database backend (SQLite or Postgres/Neon) is selected at startup via
the DB_BACKEND environment variable — see config.py.
"""

from flask import Flask, jsonify, request
from db.factory import create_backend

app = Flask(__name__)
db = create_backend()


# ── Health ────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


# ── Name lookup & trends ─────────────────────────────────────────────────

@app.route("/api/names/<name>", methods=["GET"])
def get_name_records(name: str):
    """Raw records for a name."""
    records = db.get_name_records(name)
    return jsonify([r.model_dump() for r in records])


@app.route("/api/names/<name>/trends", methods=["GET"])
def get_name_trends(name: str):
    """Yearly trend data, optional ?gender=M|F."""
    gender = request.args.get("gender")
    trends = db.get_name_trends(name, gender=gender)
    return jsonify([t.model_dump() for t in trends])


@app.route("/api/names/<name>/stats", methods=["GET"])
def get_name_stats(name: str):
    """Aggregate statistics for a name."""
    stats = db.get_name_stats(name)
    if stats is None:
        return jsonify({"error": "Name not found"}), 404
    return jsonify(stats.model_dump())


@app.route("/api/names/<name>/gender", methods=["GET"])
def get_gender_breakdown(name: str):
    """Gender breakdown for a name."""
    breakdown = db.get_gender_breakdown(name)
    return jsonify([b.model_dump() for b in breakdown])


@app.route("/api/names/<name>/decades", methods=["GET"])
def get_decade_trends(name: str):
    """Decade-aggregated trend data, optional ?gender=M|F."""
    gender = request.args.get("gender")
    decades = db.get_decade_trends(name, gender=gender)
    return jsonify([d.model_dump() for d in decades])


# ── Rankings ──────────────────────────────────────────────────────────────

@app.route("/api/rankings/<int:year>", methods=["GET"])
def get_top_names(year: int):
    """Top names for a year, optional ?gender=M|F&limit=10."""
    gender = request.args.get("gender")
    limit = request.args.get("limit", 10, type=int)
    top = db.get_top_names(year, gender=gender, limit=limit)
    return jsonify([t.model_dump() for t in top])


@app.route("/api/rankings/<int:year>/<name>", methods=["GET"])
def get_name_rank(year: int, name: str):
    """Rank of a name in a given year. Requires ?gender=M|F."""
    gender = request.args.get("gender")
    if not gender:
        return jsonify({"error": "gender query parameter is required"}), 400
    rank = db.get_name_rank(name, year, gender)
    if rank is None:
        return jsonify({"error": "Name not ranked in that year"}), 404
    return jsonify({"name": name, "year": year, "gender": gender, "rank": rank})


# ── State-level data ─────────────────────────────────────────────────────

@app.route("/api/names/<name>/states", methods=["GET"])
def get_name_by_state(name: str):
    """State-level records, optional ?state=CA."""
    state = request.args.get("state")
    records = db.get_name_by_state(name, state=state)
    return jsonify([r.model_dump() for r in records])


@app.route("/api/names/<name>/state-distribution", methods=["GET"])
def get_state_distribution(name: str):
    """Aggregate count per state for a name (good for choropleth maps)."""
    dist = db.get_state_distribution(name)
    return jsonify([d.model_dump() for d in dist])


# ── Search / autocomplete ────────────────────────────────────────────────

@app.route("/api/search", methods=["GET"])
def search_names():
    """Prefix search, required ?q=<prefix>&limit=20."""
    prefix = request.args.get("q", "")
    if len(prefix) < 1:
        return jsonify({"error": "query parameter 'q' is required"}), 400
    limit = request.args.get("limit", 20, type=int)
    results = db.search_names(prefix, limit=limit)
    return jsonify([r.model_dump() for r in results])


# ── Diversity metrics ─────────────────────────────────────────────────────

@app.route("/api/diversity", methods=["GET"])
def get_unique_name_count():
    """Number of distinct names, optional ?year=2020."""
    year = request.args.get("year", type=int)
    count = db.get_unique_name_count(year)
    return jsonify({"unique_names": count, "year": year})


# ── Legacy endpoint (backwards compatibility) ────────────────────────────

@app.route("/searchName/<name>", methods=["GET"])
def search_name_legacy(name: str):
    records = db.get_name_records(name)
    return jsonify([r.model_dump() for r in records])


# ── Entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)

