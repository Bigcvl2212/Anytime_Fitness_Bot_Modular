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
import base64
import unicodedata
from collections import defaultdict
from datetime import datetime, timedelta
from flask import Flask, request, abort

# Load environment variables first - use relative imports within src
from .config.environment_setup import load_environment_variables, validate_environment_setup

# Imports - use relative imports within src package
from .config.settings import create_app_config
from .config.constants import (
    MAX_REQUEST_SIZE_BYTES,
    RATE_LIMIT_WINDOW_SECONDS,
    MAX_REQUESTS_PER_WINDOW,
    SUSPICIOUS_REQUEST_LIMIT,
    SYNC_INTERVAL_SECONDS
)
from .config.security_middleware import (
    configure_security_headers, 
    configure_request_validation,
    configure_rate_limiting,
    configure_compression
)
from .config.error_handlers import configure_error_handlers

# Rate limiting storage (in-memory, use Redis for production)
request_counts = defaultdict(list)

# Enhanced request sanitization with comprehensive security checks
def check_xss(value: str) -> bool:
    """Detect XSS patterns including encoded variants"""
    xss_patterns = [
        '<script', '</script', 'javascript:', 'onerror=',
        'onload=', 'onclick=', '<iframe', 'eval(',
        'expression(', '<object', '<embed', 'onmouseover=',
        'onfocus=', 'oninput=', 'onchange='
    ]
    value_lower = value.lower()
    return any(pattern in value_lower for pattern in xss_patterns)

def check_sql_injection(value: str) -> bool:
    """Detect SQL injection patterns"""
    sql_patterns = [
        'union select', 'drop table', 'insert into',
        'delete from', '1=1', '1\'=\'1', 'or 1=1',
        'exec(', 'execute(', 'xp_cmdshell', '--', ';--',
        'union all', 'and 1=1', 'or \'1\'=\'1'
    ]
    value_lower = value.lower()
    return any(pattern in value_lower for pattern in sql_patterns)

def check_path_traversal(value: str) -> bool:
    """Detect path traversal attempts"""
    dangerous_patterns = [
        '../', '..\\', '%2e%2e%2f', '%2e%2e/',
        '..%2f', '%252e%252e%252f', '....',
        'file://', '/etc/', 'c:\\', 'windows\\system32'
    ]
    value_lower = value.lower()
    return any(pattern in value_lower for pattern in dangerous_patterns)

def check_base64_attacks(value: str) -> bool:
    """Detect Base64-encoded malicious content"""
    try:
        # Check if value looks like Base64 (length divisible by 4, reasonable length)
        if len(value) > 20 and len(value) % 4 == 0:
            decoded = base64.b64decode(value, validate=True).decode('utf-8', errors='ignore')
            if check_xss(decoded) or check_sql_injection(decoded):
                return True
    except Exception:
        pass
    return False

def check_template_injection(value: str) -> bool:
    """Detect Server-Side Template Injection (SSTI)"""
    ssti_patterns = ['{{', '}}', '{%', '%}', '<%', '%>', '#{', '${']
    return any(pattern in value for pattern in ssti_patterns)

def check_header_injection() -> bool:
    """Validate HTTP headers for command injection"""
    # User-Agent excluded since it legitimately contains semicolons and other special chars
    suspicious_headers = ['X-Forwarded-For', 'Referer', 'X-Real-IP']
    cmd_patterns = ['$(', '`', '|', '&&', '||', ';', '\n', '\r', '\x00']

    for header in suspicious_headers:
        value = request.headers.get(header, '')
        if any(pattern in value for pattern in cmd_patterns):
            logger.warning(f"🚨 Command injection attempt in header {header}: {value[:100]}")
            return True
    return False

def check_rate_limit(ip_address: str, is_suspicious: bool = False) -> bool:
    """Check if IP has exceeded rate limits"""
    now = datetime.now()
    window_start = now - timedelta(seconds=RATE_LIMIT_WINDOW_SECONDS)

    # Clean old requests
    request_counts[ip_address] = [
        req_time for req_time in request_counts[ip_address]
        if req_time > window_start
    ]

    # Add current request
    request_counts[ip_address].append(now)

    # Check limits
    limit = SUSPICIOUS_REQUEST_LIMIT if is_suspicious else MAX_REQUESTS_PER_WINDOW
    if len(request_counts[ip_address]) > limit:
        logger.warning(f"🚨 Rate limit exceeded for {ip_address}: {len(request_counts[ip_address])} requests in {RATE_LIMIT_WINDOW_SECONDS}s")
        return True
    return False

def add_request_sanitization(app):
    """
    Enhanced request sanitization middleware with comprehensive security checks

    Protects against:
    - XSS (Cross-Site Scripting)
    - SQL Injection
    - Path Traversal
    - Base64-encoded attacks
    - Template Injection (SSTI)
    - Command Injection in headers
    - Brute force via rate limiting
    """
    @app.before_request
    def sanitize_request():
        """Comprehensive request sanitization"""
        ip_address = request.remote_addr
        is_suspicious = False

        # 1. Large request check
        content_length = request.content_length or 0
        if content_length > MAX_REQUEST_SIZE_BYTES:
            logger.warning(f"⚠️ Large request from {ip_address}: {content_length} bytes")
            is_suspicious = True

        # 2. Command injection in headers
        if check_header_injection():
            is_suspicious = True

        # 3. Validate request data
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.form:
                for key, value in request.form.items():
                    if isinstance(value, str):
                        # Unicode normalization (prevent bypass via fullwidth characters)
                        normalized_value = unicodedata.normalize('NFKC', value)

                        # XSS detection
                        if check_xss(normalized_value):
                            logger.warning(f"🚨 XSS attempt from {ip_address}: {key}={normalized_value[:100]}")
                            is_suspicious = True

                        # SQL injection
                        if check_sql_injection(normalized_value):
                            logger.warning(f"🚨 SQL injection from {ip_address}: {key}={normalized_value[:100]}")
                            is_suspicious = True

                        # Path traversal
                        if check_path_traversal(normalized_value):
                            logger.warning(f"🚨 Path traversal from {ip_address}: {key}={normalized_value[:100]}")
                            is_suspicious = True

                        # Base64 encoded attacks
                        if check_base64_attacks(value):
                            logger.warning(f"🚨 Base64 encoded attack from {ip_address}: {key}")
                            is_suspicious = True

                        # Template injection
                        if check_template_injection(normalized_value):
                            logger.warning(f"🚨 Template injection from {ip_address}: {key}={normalized_value[:100]}")
                            is_suspicious = True

        # 4. Rate limiting (stricter for suspicious requests)
        if check_rate_limit(ip_address, is_suspicious):
            abort(429)  # Too Many Requests

    logger.info("✅ Enhanced request sanitization middleware configured")

from .monitoring import register_monitoring, run_startup_health_check
from .services.database_manager import DatabaseManager
from .services.training_package_cache import TrainingPackageCache
from .services.clubos_integration import ClubOSIntegration
from .services.performance_cache import setup_cache_cleanup_task, performance_cache
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
# CRITICAL: Use writable directory when frozen (Program Files is read-only)
try:
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - use user's AppData
        from pathlib import Path
        log_dir = Path.home() / 'AppData' / 'Local' / 'GymBot' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f'Log directory created in AppData: {log_dir}')
    else:
        # Running as script - use project directory
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        logger.info('Log directory created in project root')
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
    # CRITICAL: When frozen, templates are bundled - don't try to create in Program Files
    templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    if not getattr(sys, 'frozen', False):
        # Only create directory when running as script (not frozen executable)
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
    else:
        # When frozen, templates should already be bundled by PyInstaller
        if not os.path.exists(templates_dir):
            logger.warning(f"Templates directory not found in bundle: {templates_dir}")
    
    # Initialize services
    with app.app_context():
        # Initialize SQLite database manager
        # CRITICAL: Use writable directory for compiled executable (Program Files is read-only)
        if getattr(sys, 'frozen', False):
            # Running as compiled executable - use user's AppData
            from pathlib import Path
            data_dir = Path.home() / 'AppData' / 'Local' / 'GymBot' / 'data'
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / 'gym_bot.db')
        else:
            # Running as script - use project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, 'gym_bot.db')

        app.db_manager = DatabaseManager(db_path=db_path)
        logger.info(f"📁 SQLite Database path: {db_path}")
        
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

            # Validate secrets before use
            if not username or len(username) < 3:
                raise ValueError("ClubOS username must be at least 3 characters")
            if not password or len(password) < 8:
                raise ValueError("ClubOS password must be at least 8 characters")

            app.messaging_client = ClubOSMessagingClient(username, password)
            logger.info("✅ ClubOS messaging client initialized with validated credentials")
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
        
        # Initialize performance cache system
        setup_cache_cleanup_task()
        logger.info("✅ Performance caching system initialized")
        
        # Log cache statistics
        cache_stats = performance_cache.get_stats()
        logger.info(f"📋 Cache statistics: {cache_stats}")
        
        # Set app performance cache reference
        app.performance_cache = performance_cache
        
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

        # Initialize Admin Service
        try:
            try:
                from .services.admin_auth_service import AdminAuthService
                from .services.authentication.secure_secrets_manager import SecureSecretsManager
            except ImportError:
                from services.admin_auth_service import AdminAuthService
                from services.authentication.secure_secrets_manager import SecureSecretsManager

            # Initialize with secrets manager if available
            secrets_manager = None
            try:
                secrets_manager = SecureSecretsManager()
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize secrets manager for admin service: {e}")

            app.admin_service = AdminAuthService(app.db_manager, secrets_manager)

            # Initialize admin system (create tables and default admin)
            app.admin_service.initialize_admin_system()

            logger.info("✅ Admin service initialized successfully")
        except Exception as e:
            app.admin_service = None
            logger.warning(f"⚠️ Admin service initialization failed: {e}")

        # Initialize AI Services
        try:
            from .services.ai.ai_service_manager import AIServiceManager
            from .services.ai.ai_context_manager import AIContextManager
            from .services.ai.database_ai_adapter import DatabaseAIAdapter
            from .services.ai.admin_ai_agent import AdminAIAgent
            from .services.ai.sales_ai_agent import SalesAIAgent

            logger.info("🤖 Initializing AI services...")

            # Initialize core AI service manager
            app.ai_service = AIServiceManager()

            # Initialize AI context manager
            app.ai_context_manager = AIContextManager(app.db_manager)

            # Initialize database AI adapter
            app.db_ai_adapter = DatabaseAIAdapter(app.db_manager, app.ai_service)

            # Initialize Admin AI Agent
            if hasattr(app, 'admin_service') and app.admin_service:
                app.admin_ai_agent = AdminAIAgent(
                    ai_service_manager=app.ai_service,
                    context_manager=app.ai_context_manager,
                    db_adapter=app.db_ai_adapter,
                    admin_service=app.admin_service
                )
                logger.info("✅ Admin AI Agent initialized")
            else:
                logger.warning("⚠️ Admin AI Agent not initialized - admin service unavailable")

            # Initialize Sales AI Agent
            app.sales_ai_agent = SalesAIAgent(
                ai_service_manager=app.ai_service,
                context_manager=app.ai_context_manager,
                db_adapter=app.db_ai_adapter,
                campaign_service=getattr(app, 'campaign_service', None),
                square_client=None,  # Will be imported as needed
                messaging_client=getattr(app, 'clubos_messaging_client', None),
                db_manager=app.db_manager
            )

            logger.info("✅ AI services initialized successfully")

        except Exception as e:
            logger.warning(f"⚠️ AI services initialization failed: {e}")
            logger.warning("🤖 AI features will not be available")

            # Set AI services to None if initialization fails
            app.ai_service = None
            app.ai_context_manager = None
            app.db_ai_adapter = None
            app.admin_ai_agent = None
            app.sales_ai_agent = None

        logger.info("✅ All services initialized successfully")
        
        # Initialize automated access monitoring system (but don't start it yet)
        # Will be started after user authentication to prevent issues during deployment
        app.monitoring_started = False
        logger.info("ℹ️ Automated access monitoring initialized but not started - will start after authentication")

        # Add helper function to start monitoring after authentication
        def start_monitoring_after_auth():
            """Start automated access monitoring after successful authentication"""
            if not app.monitoring_started:
                try:
                    try:
                        from .services.automated_access_monitor import start_global_monitoring
                    except ImportError:
                        from services.automated_access_monitor import start_global_monitoring

                    # Start monitoring in a separate thread
                    def monitoring_thread():
                        try:
                            start_global_monitoring()
                            logger.info("🔐 Automated access monitoring started after authentication")
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to start automated access monitoring: {e}")

                    thread = threading.Thread(target=monitoring_thread, daemon=True)
                    thread.start()
                    app.monitoring_started = True

                except Exception as e:
                    logger.warning(f"⚠️ Automated access monitoring start failed: {e}")

        app.start_monitoring_after_auth = start_monitoring_after_auth
        
        # Run startup health checks (non-breaking)
        try:
            run_startup_health_check(app)
        except Exception as e:
            logger.warning(f"⚠️ Startup health check failed: {e}")
        
        # Don't run startup sync automatically - wait for user authentication
        # Startup sync will be triggered manually via the enhanced multi-club sync
    
    # Initialize Flask-SocketIO for real-time messaging (Phase 1)
    try:
        from flask_socketio import SocketIO
        
        # Initialize SocketIO with CORS support
        socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='threading',
            logger=True,
            engineio_logger=False
        )
        app.socketio = socketio
        logger.info("✅ Flask-SocketIO initialized for real-time messaging")
        
        # Register WebSocket handlers
        try:
            from .routes.inbox_websocket import register_websocket_handlers
            register_websocket_handlers(socketio)
            logger.info("✅ WebSocket handlers registered")
        except Exception as e:
            logger.warning(f"⚠️ WebSocket handler registration failed: {e}")
        
        # Initialize Real-Time Message Polling Service (Phase 1)
        if app.messaging_client and app.db_manager:
            try:
                from .services.real_time_message_sync import RealTimeMessageSync
                
                # Initialize polling service
                app.message_poller = RealTimeMessageSync(
                    clubos_client=app.messaging_client,
                    db_manager=app.db_manager,
                    socketio=socketio,
                    poll_interval=10  # 10 seconds
                )
                
                # Start polling in background
                app.message_poller.start_polling()
                logger.info("✅ Real-time message polling service started (10s interval)")
                
            except Exception as e:
                logger.warning(f"⚠️ Message polling service initialization failed: {e}")
                app.message_poller = None
        else:
            logger.warning("⚠️ Message polling service not started (missing dependencies)")
            app.message_poller = None
            
    except Exception as e:
        logger.warning(f"⚠️ Flask-SocketIO initialization failed: {e}")
        app.socketio = None
        app.message_poller = None
    
    # Initialize Phase 2 Workflow Scheduler and Phase 3 Agent
    try:
        from .services.ai.agent_core import GymAgentCore
        from .services.ai.workflow_scheduler import WorkflowScheduler
        from routes.ai_workflows import init_scheduler
        from routes.ai_conversation import init_agent
        
        logger.info("🤖 Initializing Phase 2 Workflow Scheduler...")
        
        # Initialize agent
        app.ai_agent = GymAgentCore()
        init_agent(app.ai_agent)
        logger.info("✅ AI Agent initialized")
        
        # Initialize workflow scheduler
        app.workflow_scheduler = WorkflowScheduler()
        init_scheduler(app.workflow_scheduler)
        logger.info("✅ Workflow Scheduler initialized")
        
        # Start scheduler (schedules will run automatically)
        app.workflow_scheduler.start()
        logger.info("🚀 Workflow Scheduler started - autonomous workflows active")
        
    except Exception as e:
        logger.warning(f"⚠️ Phase 2/3 AI initialization failed: {e}")
        app.ai_agent = None
        app.workflow_scheduler = None
    
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
            time.sleep(SYNC_INTERVAL_SECONDS)

            logger.info("🔄 Performing periodic enhanced multi-club sync...")

            # Use the same enhanced startup sync for periodic updates
            enhanced_startup_sync(app)

        except Exception as e:
            logger.error(f"❌ Periodic sync error: {e}")
            time.sleep(60)  # Wait 1 minute on error before retrying

# Remove the local app instance creation and run block.
# The app is now created and run exclusively from run_dashboard.py.
