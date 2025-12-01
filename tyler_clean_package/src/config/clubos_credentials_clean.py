#!/usr/bin/env python3
"""
ClubOS credentials configuration.

This module provides ClubOS authentication credentials.
For production, set these as environment variables or update the values below.
"""

import os

# Get credentials from environment variables or real credential files
# Try to get credentials from multiple sources
CLUBOS_USERNAME = None
CLUBOS_PASSWORD = None

# Try environment variables first
CLUBOS_USERNAME = os.getenv('CLUBOS_USERNAME')
CLUBOS_PASSWORD = os.getenv('CLUBOS_PASSWORD')

# If not in environment, try to import from credentials files
if not CLUBOS_USERNAME or not CLUBOS_PASSWORD:
    try:
        # Try the root config directory
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from config.clubhub_credentials import CLUBOS_USERNAME as REAL_USERNAME, CLUBOS_PASSWORD as REAL_PASSWORD
        CLUBOS_USERNAME = CLUBOS_USERNAME or REAL_USERNAME
        CLUBOS_PASSWORD = CLUBOS_PASSWORD or REAL_PASSWORD
    except ImportError:
        pass

# If still not found, try secrets_local
if not CLUBOS_USERNAME or not CLUBOS_PASSWORD:
    try:
        from .secrets_local import get_secret
        CLUBOS_USERNAME = CLUBOS_USERNAME or get_secret('clubos-username')
        CLUBOS_PASSWORD = CLUBOS_PASSWORD or get_secret('clubos-password')
    except ImportError:
        pass

# Use SecureSecretsManager if still not found
if not CLUBOS_USERNAME or not CLUBOS_PASSWORD:
    try:
        from ..services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        CLUBOS_USERNAME = CLUBOS_USERNAME or secrets_manager.get_secret('clubos-username')
        CLUBOS_PASSWORD = CLUBOS_PASSWORD or secrets_manager.get_secret('clubos-password')
    except ImportError:
        pass

def is_configured() -> bool:
    """Check if ClubOS credentials are properly configured"""
    return (CLUBOS_USERNAME and CLUBOS_PASSWORD and 
            not CLUBOS_USERNAME.startswith('REPLACE_WITH_REAL_') and
            not CLUBOS_PASSWORD.startswith('REPLACE_WITH_REAL_'))