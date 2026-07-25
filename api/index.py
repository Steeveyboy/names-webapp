"""
Vercel serverless entry point.

Adds the `rest/` package to sys.path so Vercel can find the FastAPI app,
then re-exports `app` so the @vercel/python runtime can serve it.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "rest"))

from app import app  # noqa: F401, E402 — re-exported for Vercel
