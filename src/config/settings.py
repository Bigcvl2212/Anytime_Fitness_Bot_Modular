#!/usr/bin/env python3
"""
Configuration settings for the Anytime Fitness Dashboard
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def create_app_config(app):
    """Configure Flask application with all necessary settings"""
    
    # Basic Flask configuration
    app.secret_key = 'anytime-fitness-dashboard-secret-key-2025'
    
    # Import Square invoice functionality with proper secrets management
    try:
        from .secrets_local import get_secret
        
        # Get Square credentials from secrets (production by default)
        access_token = get_secret("square-production-access-token")
        location_id = get_secret("square-production-location-id")
        
        # Only set environment variables if we have valid credentials
        if access_token and location_id:
            os.environ['SQUARE_PRODUCTION_ACCESS_TOKEN'] = access_token
            os.environ['SQUARE_LOCATION_ID'] = location_id
            os.environ['SQUARE_ENVIRONMENT'] = 'production'
            
            # Now import the Square function
            from ..services.payments.square_client_simple import create_square_invoice
            
            app.config['SQUARE_AVAILABLE'] = True
            app.config['SQUARE_CLIENT'] = create_square_invoice
            logger.info("🔑 Using Square credentials from secrets_local.py")
            logger.info("✅ Square client loaded successfully in PRODUCTION mode")
        else:
            # Credentials missing - use fallback
            logger.warning("⚠️ Square credentials not found in secrets")
            app.config['SQUARE_AVAILABLE'] = False
            
            # Create a fallback function
            def create_square_invoice(member_name, amount, description="Overdue Payment"):
                """Fallback Square invoice function when service is unavailable"""
                logger.error("Square service unavailable - cannot create invoice")
                return None
            
            app.config['SQUARE_CLIENT'] = create_square_invoice
        
    except ImportError as e:
        logger.warning(f"Square client not available: {e}")
        app.config['SQUARE_AVAILABLE'] = False
        
        # Create a fallback function
        def create_square_invoice(member_name, amount, description="Overdue Payment"):
            """Fallback Square invoice function when service is unavailable"""
            logger.error("Square service unavailable - cannot create invoice")
            return None
        
        app.config['SQUARE_CLIENT'] = create_square_invoice
    
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
