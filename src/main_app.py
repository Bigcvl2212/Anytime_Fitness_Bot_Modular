#!/usr/bin/env python3
"""
Clean Anytime Fitness Dashboard - Main Application
Main entry point for the Flask application
"""

import os
import sys
import logging
import threading
import time
from flask import Flask
from datetime import datetime

# Load environment variables first - use relative imports within src
from .config.environment_setup import load_environment_variables, validate_environment_setup

# Imports - use relative imports within src package
from .config.settings import create_app_config
from .config.security_middleware import (
    configure_security_headers, 
    configure_request_validation,
    configure_rate_limiting,
    configure_compression
)
from .config.error_handlers import configure_error_handlers

# Inline request sanitization (replacement for utils.validation)
def add_request_sanitization(app):
    """
    Add request sanitization middleware to Flask app
    """
    @app.before_request
    def sanitize_request():
        """Sanitize request data before processing"""
        if request.method in ['POST', 'PUT', 'PATCH']:
            # Log suspicious requests
            content_length = request.content_length or 0
            if content_length > 10 * 1024 * 1024:  # 10MB
                logger.warning(f"Large request from {request.remote_addr}: {content_length} bytes")

            # Check for suspicious patterns in form data
            if request.form:
                for key, value in request.form.items():
                    if isinstance(value, str):
                        # Check for potential script injection
                        if '<script' in value.lower() or 'javascript:' in value.lower():
                            logger.warning(f"Potential XSS attempt from {request.remote_addr}: {key}={value[:100]}...")

                        # Check for SQL injection patterns
                        sql_patterns = ['union select', 'drop table', 'insert into', 'delete from']
                        if any(pattern in value.lower() for pattern in sql_patterns):
                            logger.warning(f"Potential SQL injection from {request.remote_addr}: {key}={value[:100]}...")

    logger.info("✅ Request sanitization middleware configured")

from .monitoring import register_monitoring, run_startup_health_check
from .services.database_manager import DatabaseManager
from .services.training_package_cache import TrainingPackageCache
from .services.clubos_integration import ClubOSIntegration
from .routes import register_blueprints

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure console streams can handle UTF-8 (Windows cp1252 workaround)
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# File logging for debugging - disabled to avoid Windows file locking issues
try:
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    logger.info('Log directory created, but file logging disabled to avoid Windows lock issues')
except Exception as e:
    logger.warning(f'Could not create log directory: {e}')

def create_app():
    """Application factory pattern for creating Flask app"""
    # Load environment variables
    load_environment_variables()
    
    # Validate environment setup
    is_valid, missing = validate_environment_setup()
    if not is_valid:
        logger.warning(f"⚠️ Missing environment variables: {missing}")
    
    # The template and static folders are now correctly found relative to the project root
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    
    # Configure the app
    create_app_config(app)
    
    # Configure security middleware
    configure_security_headers(app)
    configure_request_validation(app)
    configure_rate_limiting(app)
    
    # Configure performance optimizations
    configure_compression(app)
    
    # Configure error handling
    configure_error_handlers(app)
    
    # Configure input validation and sanitization
    add_request_sanitization(app)
    
    # Register production monitoring system (non-breaking)
    register_monitoring(app)
    
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Initialize services
    with app.app_context():
        # Initialize database manager (will use environment variables to determine database type)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(project_root, 'gym_bot.db')
        
        # Pass db_path only if using SQLite, otherwise let DatabaseManager use PostgreSQL config from env
        db_type = os.getenv('DB_TYPE', 'sqlite').lower()
        if db_type == 'postgresql':
            app.db_manager = DatabaseManager()  # No db_path - will use PostgreSQL from env vars
            logger.info(f"🐘 Database configured for PostgreSQL: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
        else:
            app.db_manager = DatabaseManager(db_path=db_path)
            logger.info(f"📁 Database path: {db_path}")
        
        # Initialize training package cache
        app.training_package_cache = TrainingPackageCache()
        
        # Initialize ClubOS Integration
        app.clubos = ClubOSIntegration()
        
        # Initialize ClubHub API Client for multi-club support
        try:
            try:
                from .services.api.clubhub_api_client import ClubHubAPIClient
            except ImportError:
                from services.api.clubhub_api_client import ClubHubAPIClient
            app.clubhub_client = ClubHubAPIClient()
            logger.info("✅ ClubHub client initialized for multi-club support")
        except Exception as e:
            logger.warning(f"⚠️ ClubHub client initialization failed: {e}")
            app.clubhub_client = None
        
        # Initialize ClubOS Messaging Client
        try:
            try:
                from .services.clubos_messaging_client_simple import ClubOSMessagingClient
                from .services.authentication.secure_secrets_manager import SecureSecretsManager
            except ImportError:
                from services.clubos_messaging_client_simple import ClubOSMessagingClient
                from services.authentication.secure_secrets_manager import SecureSecretsManager
            
            secrets_manager = SecureSecretsManager()
            username = secrets_manager.get_secret('clubos-username')
            password = secrets_manager.get_secret('clubos-password')
            
            if username and password:
                app.messaging_client = ClubOSMessagingClient(username, password)
                logger.info("✅ ClubOS messaging client initialized")
            else:
                app.messaging_client = None
                logger.warning("⚠️ ClubOS messaging client not initialized - credentials missing")
        except Exception as e:
            app.messaging_client = None
            logger.warning(f"⚠️ ClubOS messaging client initialization failed: {e}")
        
        # Initialize global status tracking
        app.data_refresh_status = {
            'is_running': False,
            'started_at': None,
            'completed_at': None,
            'progress': 0,
            'status': 'idle',
            'message': 'No refresh in progress',
            'error': None
        }
        
        # Initialize data cache for persistence between page navigations
        app.data_cache = {
            'messages': [],
            'members': [],
            'prospects': [],
            'training_clients': [],
            'last_sync': {},
            'cache_timestamp': datetime.now().isoformat()
        }
        
        app.bulk_checkin_status = {
            'is_running': False,
            'started_at': None,
            'completed_at': None,
            'progress': 0,
            'total_members': 0,
            'processed_members': 0,
            'ppv_excluded': 0,
            'total_checkins': 0,
            'current_member': '',
            'status': 'idle',
            'message': 'No bulk check-in in progress',
            'error': None,
            'errors': []
        }
        
        # Initialize Campaign Service
        try:
            try:
                from .services.campaign_service import CampaignService
            except ImportError:
                from services.campaign_service import CampaignService
            
            app.campaign_service = CampaignService(app.db_manager)
            logger.info("✅ Campaign service initialized")
        except Exception as e:
            app.campaign_service = None
            logger.warning(f"⚠️ Campaign service initialization failed: {e}")
        
        logger.info("✅ All services initialized successfully")
        
        # Initialize and start automated access monitoring system
        try:
            try:
                from .services.automated_access_monitor import start_global_monitoring
            except ImportError:
                from services.automated_access_monitor import start_global_monitoring
            
            # Start monitoring in a separate thread to avoid blocking app startup
            def delayed_monitoring_start():
                time.sleep(5)  # Wait 5 seconds for app to fully initialize
                try:
                    start_global_monitoring()
                    logger.info("🔐 Automated access monitoring started successfully")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to start automated access monitoring: {e}")
            
            monitoring_thread = threading.Thread(target=delayed_monitoring_start, daemon=True)
            monitoring_thread.start()
            
        except Exception as e:
            logger.warning(f"⚠️ Automated access monitoring initialization failed: {e}")
        
        # Run startup health checks (non-breaking)
        try:
            run_startup_health_check(app)
        except Exception as e:
            logger.warning(f"⚠️ Startup health check failed: {e}")
        
        # Don't run startup sync automatically - wait for user authentication
        # Startup sync will be triggered manually via the enhanced multi-club sync
    
    # Register blueprints
    register_blueprints(app)
    
    return app

def enhanced_startup_sync(app):
    """Enhanced startup sync with multi-club support and comprehensive agreement processing"""
    logger.info("🚀 Starting enhanced multi-club startup sync...")
    
    try:
        # Import the enhanced startup sync from multi-club module
        try:
            from .services.multi_club_startup_sync import enhanced_startup_sync as multi_club_sync
        except ImportError:
            from src.services.multi_club_startup_sync import enhanced_startup_sync as multi_club_sync
        
        # Always use enhanced multi-club sync (handles both single and multi-club scenarios)
        sync_results = multi_club_sync(app, multi_club_enabled=True)
        
        if sync_results['success']:
            logger.info("� Enhanced multi-club startup sync completed successfully!")
            logger.info(f"📊 Combined totals: {sync_results['combined_totals']}")
            
            # Save data to database if available
            if hasattr(app, 'db_manager'):
                try:
                    # Save members with comprehensive billing data
                    if hasattr(app, 'cached_members') and app.cached_members:
                        app.db_manager.save_members_to_db(app.cached_members)
                        logger.info(f"✅ Database: {len(app.cached_members)} members saved with billing data")
                    
                    # Save prospects
                    if hasattr(app, 'cached_prospects') and app.cached_prospects:
                        app.db_manager.save_prospects_to_db(app.cached_prospects)
                        logger.info(f"✅ Database: {len(app.cached_prospects)} prospects saved")
                        
                    # Save training clients
                    if hasattr(app, 'cached_training_clients') and app.cached_training_clients:
                        app.db_manager.save_training_clients_to_db(app.cached_training_clients)
                        logger.info(f"✅ Database: {len(app.cached_training_clients)} training clients saved")
                        
                except Exception as db_e:
                    logger.warning(f"⚠️ Database save error: {db_e}")
        else:
            logger.error(f"❌ Enhanced startup sync failed: {sync_results.get('errors', [])}")
            
    except ImportError as e:
        logger.error(f"❌ Multi-club sync not available: {e}")
    except Exception as e:
        logger.error(f"❌ Enhanced startup sync error: {e}")

def periodic_sync(app):
    """Periodically sync data in the background using enhanced multi-club sync"""
    logger.info("🔄 Starting periodic sync thread...")
    
    while True:
        try:
            time.sleep(300)  # Sync every 5 minutes
            
            logger.info("🔄 Performing periodic enhanced multi-club sync...")
            
            # Use the same enhanced startup sync for periodic updates
            enhanced_startup_sync(app)
            
        except Exception as e:
            logger.error(f"❌ Periodic sync error: {e}")
            time.sleep(60)  # Wait 1 minute on error before retrying

# Remove the local app instance creation and run block.
# The app is now created and run exclusively from run_dashboard.py.
