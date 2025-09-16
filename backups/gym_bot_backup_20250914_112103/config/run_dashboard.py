#!/usr/bin/env python3
"""
Clean Anytime Fitness Dashboard - Entry Point
Run this script from the project root to start the dashboard
"""

import os
import sys
import logging
import urllib3

# Suppress SSL warnings globally
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ensure project root is on sys.path so 'src' is imported as a package
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Import and create the app from the src package with authentication
    from src.main_app import create_app
    app = create_app()  # Create app instance for both import and direct run
    
    if __name__ == '__main__':
        logger.info("🚀 Starting Anytime Fitness Dashboard with Authentication...")
        app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
        
except ImportError as e:
    logger.error(f"❌ Failed to import modules: {e}")
    logger.error("Make sure you're running this script from the project root directory and that 'src' is a package with __init__.py")
    app = None
    sys.exit(1)
except Exception as e:
    logger.error(f"❌ Failed to start dashboard: {e}")
    sys.exit(1)
