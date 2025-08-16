"""Minimal package shim to expose the Flask app as `app` package.
This keeps existing top-level modules (e.g., clean_dashboard.py) and lets WSGI/gunicorn import `app.app`.
"""
import importlib

# Import the top-level clean_dashboard module and expose its Flask app
_clean = importlib.import_module('clean_dashboard')
app = getattr(_clean, 'app')

__all__ = ['app']
