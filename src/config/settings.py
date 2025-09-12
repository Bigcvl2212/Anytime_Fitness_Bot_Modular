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
    
    # Basic Flask configuration
    app.secret_key = 'anytime-fitness-dashboard-secret-key-2025'
    
    # Configure Flask sessions (secure client-side cookies)
    app.config['SESSION_PERMANENT'] = True  # Allow persistent sessions
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_COOKIE_NAME'] = 'anytime_fitness_session'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_PATH'] = '/'
    app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow localhost
    
    # Set session timeout to 8 hours
    from datetime import timedelta
    app.permanent_session_lifetime = timedelta(hours=8)

    # Use Flask's default signed cookie sessions (no external storage needed)
    # This stores session data in secure signed cookies on the client side
    
    # Import Square invoice functionality - ENABLED
    try:
        # Initialize variables
        access_token = None
        location_id = None
        
        # First try SecureSecretsManager
        try:
            from ..services.authentication.secure_secrets_manager import SecureSecretsManager
            secrets_manager = SecureSecretsManager()
            access_token = secrets_manager.get_secret("square-production-access-token")
            location_id = secrets_manager.get_secret("square-production-location-id")
            
            # Validate secrets were found
            if access_token and location_id:
                logger.info("✅ Using Square credentials from SecureSecretsManager")
            else:
                missing_secrets = []
                if not access_token:
                    missing_secrets.append("square-production-access-token")
                if not location_id:
                    missing_secrets.append("square-production-location-id")
                raise ValueError(f"Missing secrets in SecretManager: {', '.join(missing_secrets)}")
                
        except Exception as secret_mgr_error:
            # Fallback to secrets_local
            logger.warning(f"❌ SecureSecretsManager failed: {secret_mgr_error}")
            logger.info("ℹ️ Falling back to secrets_local.py...")
            from .secrets_local import get_secret
            access_token = get_secret("square-production-access-token")
            location_id = get_secret("square-production-location-id")
            
            # Validate fallback secrets
            if access_token and location_id:
                logger.info("✅ Using Square credentials from secrets_local.py (fallback)")
            else:
                missing_local = []
                if not access_token:
                    missing_local.append("square-production-access-token")
                if not location_id:
                    missing_local.append("square-production-location-id")
                raise ValueError(f"Missing secrets in local config: {', '.join(missing_local)}")
        
        # Validate we have both required secrets before proceeding
        if not access_token or not location_id:
            raise ValueError("Square credentials are incomplete - missing access token or location ID")
            
        from src.services.payments.square_client_simple import create_square_invoice
        
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
    app.config['DATABASE_PATH'] = 'gym_bot.db'
    app.config['DATABASE_REFRESH_INTERVAL'] = 3600  # 1 hour in seconds
    
    # API configuration
    app.config['CLUBOS_REFRESH_INTERVAL'] = 60  # 1 minute
    app.config['TRAINING_CACHE_EXPIRY_HOURS'] = 24
    
    # Background job configuration
    app.config['PERIODIC_UPDATE_INTERVAL'] = 21600  # 6 hours
    app.config['BULK_CHECKIN_BATCH_SIZE'] = 10
    
    # Logging configuration
    app.config['LOG_LEVEL'] = 'INFO'
    app.config['LOG_FILE'] = 'logs/dashboard.log'
    app.config['LOG_MAX_BYTES'] = 2_000_000
    app.config['LOG_BACKUP_COUNT'] = 3
    
    logger.info("✅ Application configuration completed")

def get_square_client():
    """Get the Square client function, either real or fallback"""
    from flask import current_app
    return current_app.config.get('SQUARE_CLIENT')

def is_square_available():
    """Check if Square integration is available"""
    from flask import current_app
    return current_app.config.get('SQUARE_AVAILABLE', False)
