#!/usr/bin/env python3
"""
Security Middleware Module

This module provides security headers, HTTPS enforcement, and other security
features for the Flask application.
"""

import os
import logging
from flask import Flask, request, redirect, url_for, abort
from flask_talisman import Talisman
from typing import Dict, Any

logger = logging.getLogger(__name__)

def configure_security_headers(app: Flask) -> None:
    """
    Configure security headers and HTTPS enforcement for the Flask app
    
    Args:
        app: Flask application instance
    """
    # Check if we're in production
    is_production = os.getenv('FLASK_ENV', 'development').lower() == 'production'
    
    # Configure Content Security Policy
    csp_config = {
        'default-src': "'self'",
        'script-src': [
            "'self'",
            "'unsafe-inline'",  # Required for inline scripts in templates
            "'unsafe-eval'",    # Required for some JavaScript libraries
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
        ],
        'frame-ancestors': "'none'",
        'base-uri': "'self'",
        'form-action': "'self'",
    }
    
    # Configure Talisman (security headers)
    talisman_config = {
        'force_https': is_production,  # Only enforce HTTPS in production
        'force_https_permanent': False,  # Use 302 redirects, not 301
        'force_file_save': True,  # Force file downloads to be saved
        'strict_transport_security': is_production,  # HSTS only in production
        'strict_transport_security_max_age': 31536000,  # 1 year
        'strict_transport_security_include_subdomains': True,
        'content_security_policy': csp_config,
        'content_security_policy_report_only': False,  # Disable report-only for now
        'referrer_policy': 'strict-origin-when-cross-origin',
        'feature_policy': {
            'geolocation': "'none'",
            'camera': "'none'",
            'microphone': "'none'",
            'payment': "'self'",  # Allow payment features for Square
        },
        'permissions_policy': {
            'geolocation': [],
            'camera': [],
            'microphone': [],
            'payment': ['self'],
        },
    }
    
    # Apply Talisman to the app
    try:
        Talisman(app, **talisman_config)
        logger.info(f"✅ Security headers configured (Production: {is_production})")
    except ImportError:
        logger.warning("⚠️ Flask-Talisman not available. Install it for production security.")
        # Fallback to basic security headers
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
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # XSS protection (legacy browsers)
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Only add HSTS in production with HTTPS
        if is_production and request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Basic CSP (less restrictive than Talisman's)
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.squareup.com https://connect.squareup.com"
        )
        
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
        
        # Initialize Flask-Limiter with correct syntax for newer versions
        limiter = Limiter(
            get_remote_address,  # key_func as first positional argument
            app=app,
            default_limits=["200 per day", "50 per hour"],
            storage_uri="memory://",  # Use memory storage for simplicity
            strategy="fixed-window"
        )
        
        # Store limiter in app for access in routes
        app.limiter = limiter
        
        logger.info("✅ Rate limiting configured with Flask-Limiter")
        
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
            
            # Check if limit exceeded (50 requests per hour)
            if len(request_counts[client_ip]) > 50:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                abort(429)  # Too Many Requests
        
        logger.info("✅ Basic rate limiting configured (fallback implementation)")

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
    
    logger.info("✅ Basic request validation configured")