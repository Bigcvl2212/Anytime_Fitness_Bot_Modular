#!/usr/bin/env python3
"""
Security Configuration Module

This module provides secure configuration settings that work with your existing
Google Secret Manager and local secrets setup. It removes hardcoded values
while maintaining backward compatibility.
"""

import os
import secrets
import logging
from typing import Optional

# Import environment setup
try:
    from .environment_setup import get_flask_secret_key, is_production_environment
except ImportError:
    # Fallback if import fails
    def get_flask_secret_key() -> str:
        return os.getenv('FLASK_SECRET_KEY') or secrets.token_urlsafe(32)
    
    def is_production_environment() -> bool:
        return os.getenv('FLASK_ENV', 'development').lower() == 'production'

# Import your existing secrets system
try:
    from .secrets_local import get_secret, is_configured
except ImportError:
    # Fallback if import fails
    def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
        return os.getenv(key.replace('-', '_').upper(), default)
    
    def is_configured(key: str) -> bool:
        return get_secret(key) is not None

logger = logging.getLogger(__name__)

class SecurityConfig:
    """
    Secure configuration management that works with your existing secrets system
    """
    
    @staticmethod
    def get_secret_key() -> str:
        """
        Get Flask secret key from environment or generate a secure one

        Returns:
            str: Secure secret key (minimum 32 characters)

        Raises:
            ValueError: If secret key is too short
        """
        # Use the centralized environment setup function
        secret_key = get_flask_secret_key()

        # Validate minimum length for security
        if not secret_key or len(secret_key) < 32:
            raise ValueError(
                f"Flask SECRET_KEY must be at least 32 characters. "
                f"Current length: {len(secret_key) if secret_key else 0}. "
                f"Set FLASK_SECRET_KEY environment variable or use secrets.token_urlsafe(32)"
            )

        return secret_key
    
    @staticmethod
    def get_database_path() -> str:
        """
        Get database path from environment or use default
        
        Returns:
            str: Database file path
        """
        return os.getenv('DATABASE_PATH', 'gym_bot.db')
    
    @staticmethod
    def is_production() -> bool:
        """
        Check if running in production mode
        
        Returns:
            bool: True if production environment
        """
        return is_production_environment()
    
    @staticmethod
    def get_session_config() -> dict:
        """
        Get secure session configuration
        
        Returns:
            dict: Session configuration options
        """
        is_prod = SecurityConfig.is_production()
        
        return {
            'SESSION_PERMANENT': True,
            'SESSION_USE_SIGNER': True,
            'SESSION_COOKIE_NAME': 'anytime_fitness_session',
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SECURE': is_prod and os.getenv('FORCE_HTTPS', '').lower() == 'true',  # Only secure cookies in production with HTTPS
            'SESSION_COOKIE_SAMESITE': 'Lax',
            'SESSION_COOKIE_PATH': '/',
            'SESSION_COOKIE_DOMAIN': None,
            'PERMANENT_SESSION_LIFETIME': 28800  # 8 hours in seconds
        }
    
    @staticmethod
    def validate_required_secrets() -> tuple[bool, list[str]]:
        """
        Validate that all required secrets are configured
        
        Returns:
            tuple: (all_valid, missing_secrets)
        """
        required_secrets = [
            'square-production-access-token',
            'square-production-location-id',
            'clubos-username', 
            'clubos-password'
        ]
        
        missing = []
        for secret in required_secrets:
            if not is_configured(secret):
                missing.append(secret)
        
        return len(missing) == 0, missing
    
    @staticmethod
    def get_logging_config() -> dict:
        """
        Get logging configuration
        
        Returns:
            dict: Logging configuration
        """
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        
        return {
            'LOG_LEVEL': log_level,
            'LOG_FILE': os.getenv('LOG_FILE', 'logs/dashboard.log'),
            'LOG_MAX_BYTES': int(os.getenv('LOG_MAX_BYTES', '2000000')),
            'LOG_BACKUP_COUNT': int(os.getenv('LOG_BACKUP_COUNT', '3'))
        }