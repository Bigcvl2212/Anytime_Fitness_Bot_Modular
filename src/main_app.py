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

# Add src to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import database and ClubOS integration
from .services.database_manager import DatabaseManager
from .services.clubos_integration import ClubOSIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def startup_sync(app):
    """Initial sync function - placeholder for now"""
    try:
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from services.api.clubhub_api_client import ClubHubAPIClient
        from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
    except ImportError:
        ClubHubAPIClient = None
        CLUBHUB_EMAIL = None
        CLUBHUB_PASSWORD = None

from flask import Flask
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import configuration and services
from .config.settings import create_app_config
from .services.database_manager import DatabaseManager
from .services.training_package_cache import TrainingPackageCache
from .services.clubos_integration import ClubOSIntegration
from .routes import register_blueprints

# Configure logging
logging.basicConfig(level=logging.INFO)
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
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    
    # Configure the app
    create_app_config(app)
    
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Initialize services
    with app.app_context():
        # Initialize database manager
        app.db_manager = DatabaseManager()
        
        # Initialize training package cache
        app.training_package_cache = TrainingPackageCache()
        
        # Initialize ClubOS Integration
        app.clubos = ClubOSIntegration()
        
        # Initialize ClubOS Messaging Client
        try:
            from services.clubos_messaging_client import ClubOSMessagingClient
            from config.secrets_local import get_secret
            
            username = get_secret('clubos-username')
            password = get_secret('clubos-password')
            
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
        
        logger.info("✅ All services initialized successfully")
        
        # Kick off startup sync in a background thread so app doesn't block
        try:
            threading.Thread(target=startup_sync, args=(app,), daemon=True).start()
            logger.info("🔄 Startup sync launched in background thread")
        except Exception as e:
            logger.warning(f"⚠️ Could not start background startup sync: {e}")
    
    # Register blueprints
    register_blueprints(app)
    
    return app

def startup_sync(app):
    """Perform initial data sync on startup - Load ALL prospects from ClubHub API"""
    logger.info("🔄 Starting initial data sync on startup...")
    
    try:
        # Sync messages
        if app.messaging_client:
            logger.info("📨 Syncing messages on startup...")
            try:
                # Use the correct method name from the messaging client
                messages = app.messaging_client.sync_messages('187032782')
                if messages:
                    # Update cache
                    app.data_cache['messages'] = messages
                    app.data_cache['last_sync']['messages'] = datetime.now().isoformat()
                    logger.info(f"✅ Startup sync: {len(messages)} messages synced and cached")
                else:
                    logger.warning("⚠️ Startup sync: No messages found")
            except Exception as e:
                logger.error(f"❌ Startup sync messages failed: {e}")
        
        # Sync prospects directly from ClubHub API (get ALL 9000+ prospects)
        logger.info("🔍 Syncing ALL prospects from ClubHub API on startup...")
        try:
            # Import with fallback paths
            try:
                from services.api.clubhub_api_client import ClubHubAPIClient
                from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
            except ImportError:
                # Fallback to root level imports
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                from services.api.clubhub_api_client import ClubHubAPIClient
                from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
            
            # Initialize ClubHub API client
            clubhub_client = ClubHubAPIClient()
            
            # Authenticate
            if clubhub_client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
                logger.info("✅ ClubHub authenticated, fetching ALL prospects...")
                
                # Get all prospects with pagination
                prospects = clubhub_client.get_all_prospects_paginated()
                
                if prospects:
                    # Process prospects to ensure full_name is set
                    for prospect in prospects:
                        prospect['full_name'] = f"{prospect.get('firstName', '')} {prospect.get('lastName', '')}".strip()
                    
                    # Cache the prospects
                    app.data_cache['prospects'] = prospects
                    app.data_cache['last_sync']['prospects'] = datetime.now().isoformat()
                    logger.info(f"✅ Startup sync: {len(prospects)} prospects synced and cached from ClubHub API")
                    
                    # Save prospects to database as well
                    try:
                        app.db_manager.save_prospects_to_db(prospects)
                        logger.info(f"✅ Startup sync: {len(prospects)} prospects saved to database")
                    except Exception as db_e:
                        logger.warning(f"⚠️ Could not save prospects to database: {db_e}")
                        
                else:
                    logger.warning("⚠️ Startup sync: No prospects returned from ClubHub API")
            else:
                logger.error("❌ ClubHub authentication failed during startup sync")
                
        except ImportError as e:
            logger.error(f"❌ Could not import ClubHub API client or credentials: {e}")
        except Exception as e:
            logger.error(f"❌ Startup sync prospects failed: {e}")
        
        # Sync members from ClubHub API
        logger.info("� Syncing members from ClubHub API on startup...")
        try:
            from services.api.clubhub_api_client import ClubHubAPIClient
            from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
            
            # Use the same authenticated client if possible, or create new one
            clubhub_client = ClubHubAPIClient()
            
            if clubhub_client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
                members = clubhub_client.get_all_members_paginated()
                
                if members:
                    # Process members to ensure full_name is set
                    for member in members:
                        member['full_name'] = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
                    
                    app.data_cache['members'] = members
                    app.data_cache['last_sync']['members'] = datetime.now().isoformat()
                    logger.info(f"✅ Startup sync: {len(members)} members synced and cached from ClubHub API")
                    
                    # Save to database as well
                    try:
                        app.db_manager.save_members_to_db(members)
                        logger.info(f"✅ Startup sync: {len(members)} members saved to database")
                    except Exception as db_e:
                        logger.warning(f"⚠️ Could not save members to database: {db_e}")
                else:
                    logger.warning("⚠️ Startup sync: No members found from ClubHub API")
            else:
                logger.error("❌ ClubHub authentication failed for members sync")
                
        except Exception as e:
            logger.error(f"❌ Startup sync members failed: {e}")
        
        # Sync training clients from ClubOS (if available)
        if app.clubos:
            logger.info("💪 Syncing training clients on startup...")
            try:
                # Get training clients from ClubOS with full package data
                training_clients = app.clubos.get_training_clients()
                if training_clients:
                    # Cache in memory
                    app.data_cache['training_clients'] = training_clients
                    app.data_cache['last_sync']['training_clients'] = datetime.now().isoformat()
                    
                    # Save to database for persistence
                    try:
                        app.db_manager.save_training_clients_to_db(training_clients)
                        logger.info(f"✅ Startup sync: {len(training_clients)} training clients synced, cached, and saved to database")
                    except Exception as db_e:
                        logger.warning(f"⚠️ Could not save training clients to database: {db_e}")
                        logger.info(f"✅ Startup sync: {len(training_clients)} training clients synced and cached (database save failed)")
                else:
                    logger.warning("⚠️ Startup sync: No training clients found")
            except Exception as e:
                logger.error(f"❌ Startup sync training clients failed: {e}")
        
        logger.info("✅ Startup sync completed")
        
        # Start periodic sync in background thread
        try:
            periodic_sync_thread = threading.Thread(target=periodic_sync, args=(app,), daemon=True)
            periodic_sync_thread.start()
            logger.info("✅ Periodic sync thread started")
        except Exception as e:
            logger.error(f"❌ Failed to start periodic sync thread: {e}")
        
    except Exception as e:
        logger.error(f"❌ Startup sync failed: {e}")

def periodic_sync(app):
    """Periodically sync data in the background"""
    logger.info("🔄 Starting periodic sync thread...")
    
    while True:
        try:
            time.sleep(300)  # Sync every 5 minutes
            
            logger.info("🔄 Performing periodic data sync...")
            
            # Sync messages
            if app.messaging_client:
                try:
                    messages = app.messaging_client.sync_messages('187032782')
                    if messages:
                        # Update cache
                        app.data_cache['messages'] = messages
                        app.data_cache['last_sync']['messages'] = datetime.now().isoformat()
                        logger.info(f"✅ Periodic sync: {len(messages)} messages synced and cached")
                except Exception as e:
                    logger.error(f"❌ Periodic sync messages failed: {e}")
            
            # Sync prospects from ClubHub API
            try:
                # Import with fallback paths
                try:
                    from services.api.clubhub_api_client import ClubHubAPIClient
                    from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
                except ImportError:
                    # Fallback to root level imports
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                    from services.api.clubhub_api_client import ClubHubAPIClient
                    from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
                
                clubhub_client = ClubHubAPIClient()
                
                if clubhub_client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
                    prospects = clubhub_client.get_all_prospects_paginated()
                    if prospects:
                        # Process prospects to ensure full_name is set
                        for prospect in prospects:
                            prospect['full_name'] = f"{prospect.get('firstName', '')} {prospect.get('lastName', '')}".strip()
                        
                        app.data_cache['prospects'] = prospects
                        app.data_cache['last_sync']['prospects'] = datetime.now().isoformat()
                        logger.info(f"✅ Periodic sync: {len(prospects)} prospects synced and cached from ClubHub API")
                        
                        # Save prospects to database as well
                        try:
                            if hasattr(app, 'db_manager'):
                                app.db_manager.save_prospects_to_db(prospects)
                                logger.info(f"✅ Periodic sync: {len(prospects)} prospects saved to database")
                            else:
                                logger.warning("⚠️ No db_manager available, skipping database save")
                        except Exception as db_e:
                            logger.warning(f"⚠️ Could not save prospects to database: {db_e}")
                            
            except Exception as e:
                logger.error(f"❌ Periodic sync prospects failed: {e}")
            
            # Sync members from ClubHub API
            try:
                # Import with fallback paths
                try:
                    from services.api.clubhub_api_client import ClubHubAPIClient
                    from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
                except ImportError:
                    # Fallback to root level imports
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                    from services.api.clubhub_api_client import ClubHubAPIClient
                    from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
                
                clubhub_client = ClubHubAPIClient()
                
                if clubhub_client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
                    members = clubhub_client.get_all_members_paginated()
                    if members:
                        # Process members to ensure full_name is set
                        for member in members:
                            member['full_name'] = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
                        
                        app.data_cache['members'] = members
                        app.data_cache['last_sync']['members'] = datetime.now().isoformat()
                        logger.info(f"✅ Periodic sync: {len(members)} members synced and cached from ClubHub API")
                        
                        # Save members to database as well
                        try:
                            if hasattr(app, 'db_manager'):
                                app.db_manager.save_members_to_db(members)
                                logger.info(f"✅ Periodic sync: {len(members)} members saved to database")
                            else:
                                logger.warning("⚠️ No db_manager available, skipping database save")
                        except Exception as db_e:
                            logger.warning(f"⚠️ Could not save members to database: {db_e}")
                            
            except Exception as e:
                logger.error(f"❌ Periodic sync members failed: {e}")
            
            # Sync training clients from ClubOS
            if app.clubos:
                try:
                    training_clients = app.clubos.get_training_clients()
                    if training_clients:
                        # Cache in memory
                        app.data_cache['training_clients'] = training_clients
                        app.data_cache['last_sync']['training_clients'] = datetime.now().isoformat()
                        
                        # Save to database for persistence
                        try:
                            if hasattr(app, 'db_manager'):
                                app.db_manager.save_training_clients_to_db(training_clients)
                                logger.info(f"✅ Periodic sync: {len(training_clients)} training clients synced, cached, and saved to database")
                            else:
                                logger.warning("⚠️ No db_manager available, skipping database save")
                                logger.info(f"✅ Periodic sync: {len(training_clients)} training clients synced and cached")
                        except Exception as db_e:
                            logger.warning(f"⚠️ Could not save training clients to database: {db_e}")
                            logger.info(f"✅ Periodic sync: {len(training_clients)} training clients synced and cached")
                except Exception as e:
                    logger.error(f"❌ Periodic sync training clients failed: {e}")
            
        except Exception as e:
            logger.error(f"❌ Periodic sync error: {e}")
            time.sleep(60)  # Wait 1 minute on error before retrying

# Create the app instance
app = create_app()

if __name__ == '__main__':
    # On Windows, Werkzeug's reloader can trigger WinError 10038 (not a socket) during restarts.
    # Keep debug features but disable the auto-reloader for stability.
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
