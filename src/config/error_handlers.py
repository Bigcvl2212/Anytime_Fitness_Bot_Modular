#!/usr/bin/env python3
"""
Error Handling Module

This module provides comprehensive error handling for the Flask application,
including custom error pages, API error responses, and logging.
"""

import os
import logging
import traceback
from flask import Flask, request, jsonify, render_template, current_app
from werkzeug.exceptions import HTTPException
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

def configure_error_handlers(app: Flask) -> None:
    """
    Configure comprehensive error handlers for the Flask app
    
    Args:
        app: Flask application instance
    """
    # Configure error logging
    if not app.debug:
        # Set up file logging for errors in production
        import logging.handlers
        import sys
        
        # CRITICAL: Use AppData when frozen (Program Files is read-only)
        if getattr(sys, 'frozen', False):
            from pathlib import Path
            log_dir = Path.home() / 'AppData' / 'Local' / 'GymBot' / 'logs'
            log_dir.mkdir(parents=True, exist_ok=True)
            log_dir = str(log_dir)
        else:
            log_dir = 'logs'
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'errors.log'),
            maxBytes=2_000_000,
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
    
    # Register error handlers
    register_http_error_handlers(app)
    register_api_error_handlers(app)
    register_application_error_handlers(app)
    
    logger.info("✅ Comprehensive error handlers configured")

def register_http_error_handlers(app: Flask) -> None:
    """Register handlers for HTTP errors"""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request errors"""
        logger.warning(f"Bad Request: {request.url} - {error}")
        return handle_error(400, "Bad Request", "The request could not be understood by the server.")
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        """Handle 401 Unauthorized errors"""
        logger.warning(f"Unauthorized access: {request.url} - {request.remote_addr}")
        return handle_error(401, "Unauthorized", "Authentication is required to access this resource.")
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbidden errors"""
        logger.warning(f"Forbidden access: {request.url} - {request.remote_addr}")
        return handle_error(403, "Forbidden", "You don't have permission to access this resource.")
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors"""
        logger.info(f"Page not found: {request.url}")
        return handle_error(404, "Page Not Found", "The requested page could not be found.")
    
    @app.errorhandler(413)
    def request_entity_too_large_error(error):
        """Handle 413 Request Entity Too Large errors"""
        logger.warning(f"Request too large: {request.url} - Content-Length: {request.content_length}")
        return handle_error(413, "Request Too Large", "The uploaded file or request is too large.")
    
    @app.errorhandler(429)
    def too_many_requests_error(error):
        """Handle 429 Too Many Requests errors"""
        logger.warning(f"Rate limit exceeded: {request.remote_addr}")
        return handle_error(429, "Too Many Requests", "You have exceeded the rate limit. Please try again later.")
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error"""
        logger.error(f"Internal Server Error: {request.url} - {error}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return handle_error(500, "Internal Server Error", "An unexpected error occurred. Please try again later.")

def register_api_error_handlers(app: Flask) -> None:
    """Register handlers for API-specific errors"""
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle unexpected exceptions"""
        if isinstance(error, HTTPException):
            return error
        
        # Log the full traceback for debugging
        logger.error(f"Unexpected error: {type(error).__name__}: {error}")
        logger.error(f"Request: {request.method} {request.url}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return appropriate response based on request type
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred',
                'status_code': 500
            }), 500
        
        return handle_error(500, "Internal Server Error", "An unexpected error occurred. Please try again later.")

def register_application_error_handlers(app: Flask) -> None:
    """Register handlers for application-specific errors"""
    
    class GymBotError(Exception):
        """Base exception for Gym Bot application"""
        def __init__(self, message: str, status_code: int = 500):
            self.message = message
            self.status_code = status_code
            super().__init__(message)
    
    class AuthenticationError(GymBotError):
        """Authentication-related errors"""
        def __init__(self, message: str = "Authentication failed"):
            super().__init__(message, 401)
    
    class ValidationError(GymBotError):
        """Validation-related errors"""
        def __init__(self, message: str = "Validation failed"):
            super().__init__(message, 400)
    
    class ExternalServiceError(GymBotError):
        """External service-related errors"""
        def __init__(self, message: str = "External service error", service: str = "unknown"):
            self.service = service
            super().__init__(f"{service}: {message}", 502)
    
    # Register the custom exception classes in the app context
    app.GymBotError = GymBotError
    app.AuthenticationError = AuthenticationError
    app.ValidationError = ValidationError
    app.ExternalServiceError = ExternalServiceError
    
    @app.errorhandler(GymBotError)
    def handle_gym_bot_error(error):
        """Handle custom Gym Bot errors"""
        logger.error(f"GymBotError: {error.message}")
        
        if request.path.startswith('/api/'):
            return jsonify({
                'error': type(error).__name__,
                'message': error.message,
                'status_code': error.status_code
            }), error.status_code
        
        return handle_error(error.status_code, type(error).__name__, error.message)

def handle_error(status_code: int, title: str, message: str) -> Tuple[str, int]:
    """
    Generate appropriate error response based on request type
    
    Args:
        status_code: HTTP status code
        title: Error title
        message: Error message
    
    Returns:
        Tuple of (response, status_code)
    """
    # Check if this is an API request
    if request.path.startswith('/api/') or request.headers.get('Content-Type') == 'application/json':
        return jsonify({
            'error': title,
            'message': message,
            'status_code': status_code,
            'path': request.path
        }), status_code
    
    # For web requests, try to render an error template
    try:
        return render_template('error.html', 
                             status_code=status_code,
                             title=title, 
                             message=message), status_code
    except Exception as template_error:
        logger.error(f"Error template rendering failed: {template_error}")
        # Fallback to plain HTML
        html_response = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{status_code} - {title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .error {{ max-width: 600px; margin: 0 auto; text-align: center; }}
                h1 {{ color: #d32f2f; }}
                .back-link {{ margin-top: 20px; }}
                .back-link a {{ color: #1976d2; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h1>{status_code} - {title}</h1>
                <p>{message}</p>
                <div class="back-link">
                    <a href="/">&larr; Back to Dashboard</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html_response, status_code

def log_security_event(event_type: str, details: Dict[str, Any]) -> None:
    """
    Log security-related events for monitoring
    
    Args:
        event_type: Type of security event
        details: Additional details about the event
    """
    security_logger = logging.getLogger('security')
    security_info = {
        'event_type': event_type,
        'timestamp': logging.Formatter().formatTime(logging.LogRecord(
            '', 0, '', 0, '', (), None
        )),
        'remote_addr': request.remote_addr if request else 'unknown',
        'user_agent': request.headers.get('User-Agent', 'unknown') if request else 'unknown',
        'details': details
    }
    security_logger.warning(f"Security Event: {security_info}")

# Context processor for error templates
def inject_error_context():
    """Inject common context for error templates"""
    return {
        'app_name': 'Gym Bot Dashboard',
        'support_email': 'support@example.com'  # Update with actual support email
    }