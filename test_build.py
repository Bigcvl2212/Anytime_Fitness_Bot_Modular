#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Testing Script
Tests that all imports work correctly before building
"""

import sys
import os

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

print("="*60)
print("GYM BOT BUILD PRE-FLIGHT CHECK")
print("="*60)
print()

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

errors = []
warnings = []
success = []

# Test 1: Check Python version
print("[CHECK] Python Version Check...")
if sys.version_info >= (3, 8):
    success.append(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
else:
    errors.append(f"Python version too old: {sys.version}. Need 3.8+")

# Test 2: Check required files exist
print("[CHECK] Required Files Check...")
required_files = [
    'run_dashboard.py',
    'gymbot_launcher.py',
    'gym_bot.spec',
    'requirements.txt',
    'src/__init__.py',
    'src/main_app.py',
    'src/config/__init__.py',
    'src/routes/__init__.py',
    'src/services/__init__.py',
]

for file in required_files:
    if os.path.exists(os.path.join(project_root, file)):
        success.append(f"Found: {file}")
    else:
        errors.append(f"Missing required file: {file}")

# Test 3: Check directories
print("[CHECK] Required Directories Check...")
required_dirs = ['templates', 'static', 'src', 'src/config', 'src/routes', 'src/services']
for dir_name in required_dirs:
    if os.path.exists(os.path.join(project_root, dir_name)):
        success.append(f"Found: {dir_name}/")
    else:
        errors.append(f"Missing required directory: {dir_name}/")

# Test 4: Test imports
print("[CHECK] Import Test...")
try:
    print("  - Testing Flask import...")
    import flask
    success.append("Flask import OK")
except ImportError as e:
    errors.append(f"Flask import failed: {e}")

try:
    print("  - Testing Flask-SocketIO import...")
    import flask_socketio
    success.append("Flask-SocketIO import OK")
except ImportError as e:
    warnings.append(f"Flask-SocketIO import failed: {e}")

try:
    print("  - Testing pandas import...")
    import pandas
    success.append("Pandas import OK")
except ImportError as e:
    errors.append(f"Pandas import failed: {e}")

try:
    print("  - Testing dotenv import...")
    import dotenv
    success.append("python-dotenv import OK")
except ImportError as e:
    warnings.append(f"python-dotenv import failed: {e}")

try:
    print("  - Testing src package import...")
    import src
    success.append("src package import OK")
except ImportError as e:
    errors.append(f"src package import failed: {e}")

try:
    print("  - Testing src.main_app import...")
    from src.main_app import create_app
    success.append("src.main_app.create_app import OK")
except ImportError as e:
    errors.append(f"src.main_app import failed: {e}")

try:
    print("  - Testing src.config import...")
    from src.config import environment_setup
    success.append("src.config import OK")
except ImportError as e:
    errors.append(f"src.config import failed: {e}")

# Test 5: Check PyInstaller
print("[CHECK] PyInstaller Check...")
try:
    import PyInstaller
    success.append("PyInstaller installed")
except ImportError:
    errors.append("PyInstaller not installed - run: pip install pyinstaller")

# Test 6: Check for common issues
print("[CHECK] Configuration Check...")
if os.path.exists('.env'):
    success.append(".env file found")
else:
    warnings.append(".env file not found - app may need environment variables")

# Print Results
print()
print("="*60)
print("RESULTS")
print("="*60)
print()

if success:
    print(f"[SUCCESS] ({len(success)} checks passed):")
    for item in success[:10]:  # Show first 10
        print(f"   * {item}")
    if len(success) > 10:
        print(f"   ... and {len(success) - 10} more")
    print()

if warnings:
    print(f"[WARNING] ({len(warnings)} warnings):")
    for item in warnings:
        print(f"   * {item}")
    print()

if errors:
    print(f"[ERROR] ({len(errors)} errors):")
    for item in errors:
        print(f"   * {item}")
    print()
    print("[FAIL] BUILD WILL FAIL - Fix errors above before building")
    sys.exit(1)
else:
    print("[PASS] ALL CHECKS PASSED - Safe to build!")
    print()
    print("Next steps:")
    print("  1. Run: python -m PyInstaller gym_bot.spec")
    print("  2. Test: dist\\GymBot\\GymBot.exe")
    print("  3. Build installer: build_windows.bat")
    sys.exit(0)
