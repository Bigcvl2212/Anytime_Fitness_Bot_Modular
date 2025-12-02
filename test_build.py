#!/usr/bin/env python3
"""Gym Bot build pre-flight checks."""

import sys
import os
from importlib import import_module

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

checks_passed = []
warnings = []
errors = []

print("=" * 70)
print("GYM BOT BUILD PRE-FLIGHT CHECK")
print("=" * 70)

# Python version
if sys.version_info >= (3, 10):
    checks_passed.append(f"Python {sys.version.split()[0]} detected")
else:
    errors.append(f"Python {sys.version.split()[0]} detected, need 3.10+")

# Required files/directories
required_paths = [
    "gymbot_main.py",
    "run_dashboard.py",
    "GymBot.spec",
    "requirements.txt",
    "installer_windows.iss",
    os.path.join("templates"),
    os.path.join("static"),
    os.path.join("src", "__init__.py"),
]

for rel_path in required_paths:
    abs_path = os.path.join(PROJECT_ROOT, rel_path)
    if os.path.exists(abs_path):
        checks_passed.append(f"Found {rel_path}")
    else:
        errors.append(f"Missing {rel_path}")

# Module import tests
modules_to_test = [
    "flask",
    "flask_socketio",
    "dotenv",
    "requests",
]

for module_name in modules_to_test:
    try:
        import_module(module_name)
        checks_passed.append(f"Import OK: {module_name}")
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"Import failed: {module_name} ({exc})")

# Project level import
try:
    from src.main_app import create_app  # noqa: F401
    checks_passed.append("Import OK: src.main_app.create_app")
except Exception as exc:  # noqa: BLE001
    errors.append(f"Failed to import src.main_app.create_app ({exc})")

# PyInstaller presence
try:
    import PyInstaller  # noqa: F401
    checks_passed.append("PyInstaller installed")
except Exception:
    errors.append("PyInstaller missing - ensure 'pip install pyinstaller'")

print("\nSummary:\n--------")
if checks_passed:
    for msg in checks_passed[:12]:
        print(f"  [OK] {msg}")
    if len(checks_passed) > 12:
        print(f"  ... and {len(checks_passed) - 12} more")

if warnings:
    print("\nWarnings:")
    for warn in warnings:
        print(f"  [WARN] {warn}")

if errors:
    print("\nErrors:")
    for err in errors:
        print(f"  [FAIL] {err}")
    print("\nBUILD ABORTED - resolve errors above")
    sys.exit(1)

print("\nAll critical checks passed. Safe to build!")
sys.exit(0)
