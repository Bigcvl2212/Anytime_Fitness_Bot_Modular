#!/usr/bin/env python3
"""
Security Middleware Module

This module provides security headers, HTTPS enforcement, and other security
features for the Flask application.
"""

import os
import logging
from flask import Flask, request, redirect, url_for, abort
from typing import Dict, Any

# Optional import for Flask-Talisman
try:
    from flask_talisman import Talisman
    TALISMAN_AVAILABLE = True
except ImportError:
    TALISMAN_AVAILABLE = False
    Talisman = None

logger = logging.getLogger(__name__)

def configure_session_security(app: Flask, is_production: bool = False) -> None:
    """
    Configure secure session cookie settings based on environment
    
    Args:
        app: Flask application instance
        is_production: Whether running in production mode
    """
    # Session cookie settings - secure only in production with HTTPS
    app.config['SESSION_COOKIE_SECURE'] = is_production
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Always prevent XSS
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
    
    # Only set secure cookies in production or when HTTPS is available
    if is_production:
        app.config['SESSION_COOKIE_NAME'] = 'anytime_fitness_session'
        logger.info("✅ Secure session cookies configured for production")
    else:
        # Development mode - allow insecure cookies for localhost
        app.config['SESSION_COOKIE_NAME'] = 'anytime_fitness_session'
        logger.info("✅ Development session cookies configured (insecure for localhost)")
    
    @app.before_request
    def handle_secure_cookies():
        """Handle secure cookie warnings in development"""
        if not is_production and request.is_secure:
            # If we're in development but somehow got HTTPS, allow secure cookies
            app.config['SESSION_COOKIE_SECURE'] = True

def configure_security_headers(app: Flask) -> None:
    """
    Configure security headers and HTTPS enforcement for the Flask app
    
    Args:
        app: Flask application instance
    """
    # Check if we're in production - NEVER force HTTPS for localhost/development
    flask_env = os.getenv('FLASK_ENV', 'development').lower()
    is_production = flask_env == 'production'
    
    # CRITICAL: Force disable HTTPS redirect for localhost/development
    # This prevents the 302 redirect loop that breaks the dashboard
    if not is_production:
        logger.info(f"🔓 Development mode detected (FLASK_ENV={flask_env}) - HTTPS redirect DISABLED")
    
    # Configure secure session cookies based on environment
    configure_session_security(app, is_production)
    
    # Configure Content Security Policy
    csp_config = {
        'default-src': "'self'",
        'script-src': [
            "'self'",
            "'unsafe-inline'",  # Required for inline scripts in templates - TODO: migrate to event listeners
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
            "https://code.jquery.com",
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",  # Required for inline styles
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
            "https://fonts.googleapis.com",
        ],
        'font-src': [
            "'self'",
            "https://fonts.gstatic.com",
            "https://cdnjs.cloudflare.com",  # Font Awesome fonts
            "data:",
        ],
        'img-src': [
            "'self'",
            "data:",
            "https:",  # Allow images from HTTPS sources
        ],
        'connect-src': [
            "'self'",
            "https://api.squareup.com",  # Square API
            "https://connect.squareup.com",  # Square Connect API
            "https://cdn.jsdelivr.net",  # Bootstrap and other CDN resources
            "https://cdnjs.cloudflare.com",  # Font Awesome and other CDN resources
        ],
        'frame-ancestors': "'none'",
        'base-uri': "'self'",
        'form-action': "'self'",
    }
    
    # Configure Talisman (security headers) - production ready
    talisman_config = {
        'force_https': is_production,  # Only enforce HTTPS in production
        'force_https_permanent': False,  # Use 302 redirects, not 301
        'force_file_save': True,  # Force file downloads to be saved
        'strict_transport_security': is_production,  # HSTS only in production
        'strict_transport_security_max_age': 31536000,  # 1 year
        'strict_transport_security_include_subdomains': True,
        'strict_transport_security_preload': is_production,  # Preload for production
        'content_security_policy': csp_config,
        'content_security_policy_report_only': False,  # Disable report-only for now
        'referrer_policy': 'strict-origin-when-cross-origin',
        'permissions_policy': {
            'geolocation': '()',
            'camera': '()',
            'microphone': '()',
            'payment': '(self)',
        },
        # Disable X-Frame-Options in favor of CSP frame-ancestors
        'frame_options': None,
        'frame_options_allow_from': None,
        # Configure secure cookie settings
        'session_cookie_secure': is_production,
        'session_cookie_http_only': True,
        'session_cookie_samesite': 'Lax',
    }
    
    # Apply Talisman to the app if available
    # CRITICAL: Skip Talisman entirely in development to avoid any HTTPS issues
    if TALISMAN_AVAILABLE and is_production:
        try:
            Talisman(app, **talisman_config)
            logger.info(f"✅ Security headers configured with Talisman (Production: {is_production})")
        except Exception as e:
            logger.warning(f"⚠️ Failed to configure Talisman: {e}. Using fallback headers.")
            configure_basic_security_headers(app, is_production)
    else:
        if not is_production:
            logger.info("🔓 Skipping Talisman in development mode to avoid HTTPS redirects")
            # Use minimal security headers in development - NO HTTPS redirects
            configure_basic_security_headers(app, False)
        else:
            logger.info("ℹ️ Flask-Talisman not available. Using basic security headers.")
            configure_basic_security_headers(app, is_production)

def configure_basic_security_headers(app: Flask, is_production: bool = False) -> None:
    """
    Configure basic security headers as a fallback when Talisman is not available
    
    Args:
        app: Flask application instance
        is_production: Whether running in production mode
    """
    @app.after_request
    def add_security_headers(response):
        """Add basic security headers to all responses"""
        # Note: X-Frame-Options removed in favor of CSP frame-ancestors directive
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # XSS protection (legacy browsers)
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Only add HSTS in production with HTTPS
        if is_production and request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Skip CSP for static resources (not needed and causes console warnings)
        is_static = (request.endpoint == 'static' or 
                    (request.path and any(request.path.endswith(ext) for ext in ['.css', '.js', '.woff', '.woff2', '.ttf', '.eot', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico'])))
        
        if not is_static:
            # Basic CSP (less restrictive than Talisman's) - only for HTML pages
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://code.jquery.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com data:; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://api.squareup.com https://connect.squareup.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
                "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
            )
        
        # Remove server version information for security (hide werkzeug/python version)
        response.headers.pop('Server', None)
        
        return response
    
    # HTTPS redirect for production
    if is_production:
        @app.before_request
        def force_https():
            """Force HTTPS in production"""
            if not request.is_secure and not request.headers.get('X-Forwarded-Proto') == 'https':
                return redirect(request.url.replace('http://', 'https://'), code=301)
    
    logger.info(f"✅ Basic security headers configured (Production: {is_production})")

def configure_rate_limiting(app: Flask) -> None:
    """
    Configure rate limiting for production security
    
    Args:
        app: Flask application instance
    """
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        
        # Initialize Flask-Limiter with higher limits for automation
        limiter = Limiter(
            get_remote_address,  # key_func as first positional argument
            app=app,
            default_limits=["1000 per day", "500 per hour"],  # Higher limits for automation systems
            storage_uri="memory://",  # Use memory storage for simplicity
            strategy="fixed-window"
        )
        
        # Store limiter in app for access in routes
        app.limiter = limiter
        
        # Define automation endpoints that need even higher limits
        automation_endpoints = [
            '/api/bulk-checkin-status',
            '/api/funding-cache-status', 
            '/api/bulk-checkin-processed-members'
        ]
        
        # Override rate limiting for automation endpoints
        @limiter.request_filter
        def exempt_automation_endpoints():
            """Exempt automation endpoints from rate limiting"""
            from flask import request
            try:
                endpoint_path = request.path
                # Check if this is an automation endpoint that should be exempt
                return any(endpoint_path.endswith(auto_endpoint) for auto_endpoint in automation_endpoints)
            except:
                return False
        
        logger.info("✅ Rate limiting configured with Flask-Limiter and higher automation limits")
        
    except ImportError:
        logger.warning("⚠️ Flask-Limiter not installed. Using basic rate limiting fallback")
        
        # Simple in-memory rate limiting fallback
        from collections import defaultdict
        import time
        
        # Track requests per IP
        request_counts = defaultdict(list)
        
        @app.before_request
        def basic_rate_limit():
            """Basic rate limiting implementation"""
            client_ip = request.environ.get('REMOTE_ADDR', 'unknown')
            current_time = time.time()
            
            # Clean old requests (older than 1 hour)
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip] 
                if current_time - req_time < 3600
            ]
            
            # Add current request
            request_counts[client_ip].append(current_time)

            # Check if limit exceeded (1000 requests per hour for normal dashboard usage)
            if len(request_counts[client_ip]) > 1000:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                abort(429)  # Too Many Requests
        
        logger.info("✅ Basic rate limiting configured (fallback implementation)")

def configure_compression(app: Flask) -> None:
    """
    Configure response compression for better performance
    
    Args:
        app: Flask application instance
    """
    try:
        from flask_compress import Compress
        
        # Configure compression settings
        app.config['COMPRESS_MIMETYPES'] = [
            'text/html', 'text/css', 'text/xml', 'text/plain',
            'application/json', 'application/javascript', 'text/javascript',
            'application/xml', 'application/rss+xml', 'application/atom+xml',
            'image/svg+xml'
        ]
        app.config['COMPRESS_LEVEL'] = 6  # Balance between compression and CPU usage
        app.config['COMPRESS_MIN_SIZE'] = 500  # Only compress files larger than 500 bytes
        
        # Initialize Flask-Compress
        Compress(app)
        logger.info("✅ Response compression configured with Flask-Compress")
        
    except ImportError:
        logger.info("ℹ️ Flask-Compress not installed. Install it for better performance: pip install Flask-Compress")

def configure_request_validation(app: Flask) -> None:
    """
    Configure basic request validation and security
    
    Args:
        app: Flask application instance
    """
    @app.before_request
    def validate_request():
        """Basic request validation"""
        # Limit request size (10MB max)
        max_content_length = 10 * 1024 * 1024  # 10MB
        if request.content_length and request.content_length > max_content_length:
            abort(413)  # Request Entity Too Large
        
        # Block requests with suspicious headers
        user_agent = request.headers.get('User-Agent', '')
        if not user_agent or len(user_agent) > 500:
            logger.warning(f"Suspicious User-Agent: {user_agent[:100]}...")
            # Don't block, just log for now
    
    @app.after_request
    def add_performance_headers(response):
        """Add proper charset to content-type headers, cache control, and compression hints"""
        # Fix content-type charset
        if response.content_type and 'application/json' in response.content_type:
            if 'charset' not in response.content_type:
                response.content_type = 'application/json; charset=utf-8'
        elif response.content_type and 'text/html' in response.content_type:
            if 'charset' not in response.content_type:
                response.content_type = 'text/html; charset=utf-8'
        
        # Enhanced cache-control headers for performance
        if not response.cache_control:
            # Static assets (CSS, JS, fonts, images) get long-term caching
            if (request.endpoint == 'static' or 
                (request.path and any(request.path.endswith(ext) for ext in ['.css', '.js', '.woff', '.woff2', '.ttf', '.eot', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']))):
                response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'  # 1 year with immutable
                # Remove CSP header from static resources (not needed)
                response.headers.pop('Content-Security-Policy', None)
                response.headers.pop('Content-Security-Policy-Report-Only', None)
            # API endpoints should have short cache
            elif request.endpoint and request.endpoint.startswith('api.'):
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                # Remove Expires header - use Cache-Control instead
            else:
                # Dynamic pages can be cached briefly - increased from 300 to 600 seconds
                response.headers['Cache-Control'] = 'public, max-age=600'  # 10 minutes
        
        # Add compression hint for compressible content
        if response.content_type:
            compressible_types = [
                'text/html', 'text/css', 'text/javascript', 'application/javascript',
                'application/json', 'text/xml', 'application/xml', 'text/plain'
            ]
            if any(ctype in response.content_type for ctype in compressible_types):
                # Modern browsers support these compression formats
                response.headers['Vary'] = 'Accept-Encoding'
        
        # Remove server version information for security (hide werkzeug/python version)
        response.headers.pop('Server', None)
        
        return response
    
    logger.info("✅ Basic request validation configured")