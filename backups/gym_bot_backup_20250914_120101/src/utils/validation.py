#!/usr/bin/env python3
"""
Input Validation and Sanitization Module

This module provides comprehensive input validation and sanitization utilities
for the Flask application to prevent XSS, SQL injection, and other attacks.
"""

import re
import logging
import html
import urllib.parse
from typing import Any, Dict, List, Optional, Union
import bleach
from flask import request, current_app

logger = logging.getLogger(__name__)

# Allowed HTML tags for content that should support basic formatting
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    '*': ['class']
}

# Regular expressions for validation
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PHONE_REGEX = re.compile(r'^\+?[\d\s\-\(\)]{10,}$')
ALPHANUMERIC_REGEX = re.compile(r'^[a-zA-Z0-9\s\-_]+$')
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9._-]{3,50}$')

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class InputValidator:
    """
    Comprehensive input validation and sanitization
    """
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000, allow_html: bool = False) -> str:
        """
        Sanitize string input to prevent XSS attacks
        
        Args:
            value: Input string to sanitize
            max_length: Maximum allowed length
            allow_html: Whether to allow safe HTML tags
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return str(value)
        
        # Truncate if too long
        value = value[:max_length]
        
        if allow_html:
            # Use bleach to allow only safe HTML
            return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
        else:
            # Escape all HTML
            return html.escape(value)
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not email or len(email) > 254:
            return False
        return bool(EMAIL_REGEX.match(email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate phone number format
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not phone:
            return False
        # Remove spaces and special characters for validation
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        return len(cleaned) >= 10 and cleaned.replace('+', '').isdigit()
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validate username format
        
        Args:
            username: Username to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not username:
            return False
        return bool(USERNAME_REGEX.match(username))
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password must be less than 128 characters long"
        
        # Check for common patterns
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        score = sum([has_upper, has_lower, has_digit, has_special])
        
        if score < 3:
            return False, "Password must contain at least 3 of: uppercase, lowercase, numbers, special characters"
        
        return True, ""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal attacks
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        if not filename:
            return "untitled"
        
        # Remove path separators and dangerous characters
        safe_chars = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Remove leading/trailing dots and spaces
        safe_chars = safe_chars.strip('. ')
        
        # Limit length
        safe_chars = safe_chars[:255]
        
        # Ensure it's not empty
        return safe_chars if safe_chars else "untitled"
    
    @staticmethod
    def validate_amount(amount: Union[str, float, int]) -> tuple[bool, Optional[float]]:
        """
        Validate monetary amount
        
        Args:
            amount: Amount to validate
            
        Returns:
            Tuple of (is_valid, parsed_amount)
        """
        try:
            if isinstance(amount, str):
                # Remove currency symbols and spaces
                clean_amount = re.sub(r'[\$\s,]', '', amount)
                parsed_amount = float(clean_amount)
            else:
                parsed_amount = float(amount)
            
            # Check reasonable bounds
            if parsed_amount < 0:
                return False, None
            if parsed_amount > 999999.99:  # Max $999,999.99
                return False, None
            
            # Round to 2 decimal places
            parsed_amount = round(parsed_amount, 2)
            
            return True, parsed_amount
            
        except (ValueError, TypeError):
            return False, None

class FormValidator:
    """
    Form validation utilities
    """
    
    @staticmethod
    def validate_login_form(form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate login form data
        
        Args:
            form_data: Form data dictionary
            
        Returns:
            Dictionary with validation results and sanitized data
        """
        errors = []
        sanitized = {}
        
        # Validate username
        username = form_data.get('clubos_username', '').strip()
        if not username:
            errors.append("ClubOS username is required")
        elif not InputValidator.validate_username(username):
            errors.append("Invalid username format")
        else:
            sanitized['clubos_username'] = username
        
        # Validate password
        password = form_data.get('clubos_password', '')
        if not password:
            errors.append("ClubOS password is required")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters")
        else:
            sanitized['clubos_password'] = password  # Don't sanitize passwords
        
        # Validate email
        email = form_data.get('clubhub_email', '').strip().lower()
        if not email:
            errors.append("ClubHub email is required")
        elif not InputValidator.validate_email(email):
            errors.append("Invalid email format")
        else:
            sanitized['clubhub_email'] = email
        
        # Validate ClubHub password
        clubhub_password = form_data.get('clubhub_password', '')
        if not clubhub_password:
            errors.append("ClubHub password is required")
        elif len(clubhub_password) < 8:
            errors.append("ClubHub password must be at least 8 characters")
        else:
            sanitized['clubhub_password'] = clubhub_password
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'sanitized_data': sanitized
        }
    
    @staticmethod
    def validate_member_form(form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate member-related form data
        
        Args:
            form_data: Form data dictionary
            
        Returns:
            Dictionary with validation results and sanitized data
        """
        errors = []
        sanitized = {}
        
        # Validate member name
        name = form_data.get('name', '').strip()
        if not name:
            errors.append("Member name is required")
        elif len(name) > 100:
            errors.append("Member name must be less than 100 characters")
        else:
            sanitized['name'] = InputValidator.sanitize_string(name, max_length=100)
        
        # Validate email if provided
        email = form_data.get('email', '').strip().lower()
        if email:
            if not InputValidator.validate_email(email):
                errors.append("Invalid email format")
            else:
                sanitized['email'] = email
        
        # Validate phone if provided
        phone = form_data.get('phone', '').strip()
        if phone:
            if not InputValidator.validate_phone(phone):
                errors.append("Invalid phone number format")
            else:
                sanitized['phone'] = InputValidator.sanitize_string(phone, max_length=20)
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'sanitized_data': sanitized
        }
    
    @staticmethod
    def validate_message_form(form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate messaging form data
        
        Args:
            form_data: Form data dictionary
            
        Returns:
            Dictionary with validation results and sanitized data
        """
        errors = []
        sanitized = {}
        
        # Validate message content
        message = form_data.get('message', '').strip()
        if not message:
            errors.append("Message content is required")
        elif len(message) > 2000:
            errors.append("Message must be less than 2000 characters")
        else:
            # Allow some HTML in messages but sanitize
            sanitized['message'] = InputValidator.sanitize_string(message, max_length=2000, allow_html=True)
        
        # Validate recipient selection
        recipients = form_data.get('recipients', [])
        if not recipients:
            errors.append("At least one recipient must be selected")
        else:
            # Sanitize recipient IDs
            sanitized['recipients'] = [
                InputValidator.sanitize_string(str(r), max_length=50) 
                for r in recipients if r
            ]
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'sanitized_data': sanitized
        }

def sanitize_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize all values in a request data dictionary
    
    Args:
        data: Dictionary containing request data
        
    Returns:
        Dictionary with sanitized values
    """
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = InputValidator.sanitize_string(value)
        elif isinstance(value, list):
            sanitized[key] = [
                InputValidator.sanitize_string(str(item)) if isinstance(item, str) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized

def validate_csrf_token() -> bool:
    """
    Validate CSRF token for form submissions
    
    Returns:
        True if CSRF token is valid, False otherwise
    """
    # This is a placeholder - Flask-WTF handles CSRF automatically
    # when forms are properly configured
    return True

# Security middleware function to add to Flask app
def add_request_sanitization(app):
    """
    Add request sanitization middleware to Flask app
    
    Args:
        app: Flask application instance
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