import os
import logging

# Configure logging for WSGI
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Import the Flask app directly - now in same directory
    from main_app import create_app
    
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
