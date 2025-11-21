import os
import sys
import logging

# Configure logging for WSGI
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure the project root is on sys.path for proper imports
ROOT_DIR = os.path.dirname(__file__)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    # Import the Flask app from the modular structure
    from src.main_app import create_app
    
    # Create the application instance
    app = create_app()
    logger.info("✅ WSGI: Flask application created successfully")
    
except ImportError as e:
    logger.error(f"❌ WSGI: Failed to import application: {e}")
    raise
except Exception as e:
    logger.error(f"❌ WSGI: Failed to create application: {e}")
    raise

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
