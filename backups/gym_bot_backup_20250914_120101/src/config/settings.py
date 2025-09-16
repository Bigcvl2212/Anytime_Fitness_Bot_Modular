#!/usr/bin/env python3
"""
Application Settings for the Anytime Fitness Dashboard
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def create_app_config(app):
    """Configure Flask application with all necessary settings"""
    
    # Import security configuration
    from .security_config import SecurityConfig
    
    # Basic Flask configuration with secure secret key
    app.secret_key = SecurityConfig.get_secret_key()
    
    # Configure Flask sessions (secure client-side cookies)
    session_config = SecurityConfig.get_session_config()
    for key, value in session_config.items():
        if key == 'PERMANENT_SESSION_LIFETIME':
            from datetime import timedelta
            app.permanent_session_lifetime = timedelta(seconds=value)
        else:
            app.config[key] = value

    # Use Flask's default signed cookie sessions (no external storage needed)
    # This stores session data in secure signed cookies on the client side
    
    # Import Square invoice functionality - ENABLED
    try:
        # Get Square credentials from SecureSecretsManager (no fallback allowed)
        from ..services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        access_token = secrets_manager.get_secret("square-production-access-token")
        location_id = secrets_manager.get_secret("square-production-location-id")
        
        # Validate both secrets are available
        if not access_token or not location_id:
            missing_secrets = []
            if not access_token:
                missing_secrets.append("square-production-access-token")
            if not location_id:
                missing_secrets.append("square-production-location-id")
            raise ValueError(f"Missing Square production secrets: {', '.join(missing_secrets)}")
        
        logger.info("✅ Using Square credentials from SecureSecretsManager")
        
        # Validate we have both required secrets before proceeding
        if not access_token or not location_id:
            raise ValueError("Square credentials are incomplete - missing access token or location ID")
            
        # Import the Square client function (not the class)
        try:
            import sys
            import os
            # Add src to path for absolute import
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.dirname(current_dir)
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            from services.payments.square_client_simple import create_square_invoice
        except ImportError as import_error:
            logger.error(f"❌ Failed to import Square client function: {import_error}")
            raise ImportError(f"Square client import failed: {import_error}")
        
        # Set environment variables (now we know they're not None)
        os.environ['SQUARE_PRODUCTION_ACCESS_TOKEN'] = access_token
        os.environ['SQUARE_LOCATION_ID'] = location_id
        os.environ['SQUARE_ENVIRONMENT'] = 'production'
        
        # Use the real Square client
        app.config['SQUARE_AVAILABLE'] = True
        app.config['SQUARE_CLIENT'] = create_square_invoice
        logger.info("✅ Square client loaded successfully in PRODUCTION mode")
        
    except ImportError as e:
        logger.warning(f"❌ Square client import failed: {e}")
        logger.info("ℹ️ Square client disabled - continuing without payment functionality")
        app.config['SQUARE_AVAILABLE'] = False
        app.config['SQUARE_CLIENT'] = None
    except Exception as e:
        logger.warning(f"❌ Square client initialization failed: {e}")
        logger.info("ℹ️ Square client disabled - continuing without payment functionality")
        app.config['SQUARE_AVAILABLE'] = False
        app.config['SQUARE_CLIENT'] = None
    
    # Database configuration
    app.config['DATABASE_PATH'] = SecurityConfig.get_database_path()
    app.config['DATABASE_REFRESH_INTERVAL'] = 3600  # 1 hour in seconds
    
    # API configuration
    app.config['CLUBOS_REFRESH_INTERVAL'] = 60  # 1 minute
    app.config['TRAINING_CACHE_EXPIRY_HOURS'] = 24
    
    # Background job configuration
    app.config['PERIODIC_UPDATE_INTERVAL'] = 21600  # 6 hours
    app.config['BULK_CHECKIN_BATCH_SIZE'] = 10
    
    # Logging configuration
    log_config = SecurityConfig.get_logging_config()
    for key, value in log_config.items():
        app.config[key] = value
    
    logger.info("✅ Application configuration completed")

def get_square_client():
    """Get the Square client function, either real or fallback"""
    from flask import current_app
    return current_app.config.get('SQUARE_CLIENT')

def is_square_available():
    """Check if Square integration is available"""
    from flask import current_app
    return current_app.config.get('SQUARE_AVAILABLE', False)
