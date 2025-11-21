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

# CRITICAL: Handle frozen (PyInstaller) vs script mode
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    # PyInstaller extracts to sys._MEIPASS
    project_root = sys._MEIPASS
    print(f"Running in FROZEN mode - Bundle path: {project_root}")
else:
    # Running as script
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"Running in SCRIPT mode - Project root: {project_root}")

# Ensure project root is on sys.path so 'src' is imported as a package
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added to sys.path: {project_root}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Import and create the app from the src package
    print("Importing src.main_app...")
    from src.main_app import create_app

    print("Creating Flask app...")
    app = create_app()  # Create app instance for both import and direct run

    print("Flask app created successfully!")

    if __name__ == '__main__':
        logger.info("Starting Anytime Fitness Dashboard...")
        logger.info(f"Server will be available at: http://localhost:5000")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Python: {sys.version}")
        logger.info(f"Frozen: {getattr(sys, 'frozen', False)}")
        
        # Start server with socketio if available
        if hasattr(app, 'socketio') and app.socketio:
            logger.info("🔌 Starting with SocketIO support...")
            app.socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        else:
            logger.info("⚡ Starting without SocketIO...")
            app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        
except ImportError as e:
    logger.error(f"❌ Failed to import modules: {e}")
    logger.error("Make sure you're running this script from the project root directory and that 'src' is a package with __init__.py")
    logger.error(f"sys.path: {sys.path}")
    logger.error(f"Current directory: {os.getcwd()}")
    import traceback
    traceback.print_exc()
    app = None
    sys.exit(1)
except Exception as e:
    logger.error(f"❌ Failed to start dashboard: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
