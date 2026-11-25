"""
Vercel serverless entry point.
Vercel's @vercel/python builder looks for an `app` WSGI application object.
"""
import os
import sys
from pathlib import Path

# Ensure the project root is on sys.path so `app` package is importable
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Force production config on Vercel
os.environ.setdefault("FLASK_ENV", "production")

from app import create_app

app = create_app()

# Vercel expects the WSGI app object named `app` — this is it.
