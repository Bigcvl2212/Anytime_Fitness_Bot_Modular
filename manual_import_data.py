#!/usr/bin/env python3
"""
Manual data import script to populate the database
"""

import os
import sys

# Set environment variable to trigger data import
os.environ['IMPORT_FRESH_DATA_ON_STARTUP'] = 'true'

# Ensure project root is on sys.path so 'src' is imported as a package
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import from the modular services
try:
    from src.services.multi_club_startup_sync import import_fresh_clubhub_data
    print("🔄 Starting manual data import using modular services...")
    import_fresh_clubhub_data()
    print("✅ Manual data import completed!")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
