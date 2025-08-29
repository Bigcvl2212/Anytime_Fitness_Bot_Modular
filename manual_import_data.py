#!/usr/bin/env python3
"""
Manual data import script to populate the database
"""

import os
import sys

# Set environment variable to trigger data import
os.environ['IMPORT_FRESH_DATA_ON_STARTUP'] = 'true'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the function directly
try:
    from clean_dashboard import import_fresh_clubhub_data
    print("🔄 Starting manual data import...")
    import_fresh_clubhub_data()
    print("✅ Manual data import completed!")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
