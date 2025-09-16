#!/usr/bin/env python3
"""
Local secrets accessor for the Anytime Fitness Dashboard.

This module provides access to sensitive configuration like API keys and credentials.
For production, set these as environment variables or create a local_secrets.json file.
"""

import json
import os
from typing import Optional

# No default credentials - must be provided via environment variables or secrets file
_DEFAULT_SECRETS = {}

def _load_json() -> dict:
    """Load secrets from JSON file if it exists"""
    candidate_files = [
        os.path.join(os.path.dirname(__file__), 'local_secrets.json'),
        os.path.join(os.getcwd(), 'src', 'config', 'local_secrets.json'),
    ]
    
    for path in candidate_files:
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            # Fail soft; defaults remain primary
            pass
    return {}

_JSON_CACHE = _load_json()

def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Return secret from environment, JSON file, or real credential files.
    
    Priority order:
    1. Environment variables (highest priority)
    2. JSON file secrets
    3. Real credential files (production)
    4. None (lowest priority)
    
    Example keys:
      - square-production-access-token
      - square-production-location-id
      - clubos-username
      - clubos-password
    """
    # Check environment variables first
    env_key = key.replace('-', '_').upper()
    if env_key in os.environ:
        return os.environ[env_key]
    
    # Check JSON file
    if key in _JSON_CACHE:
        return _JSON_CACHE[key]
    
    # Use SecureSecretsManager for production credentials
    try:
        from ..services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        value = secrets_manager.get_secret(key)
        if value:
            return value
    except ImportError:
        pass
    
    # Return None if not found
    return None

def is_configured(key: str) -> bool:
    """Check if a secret is properly configured (not placeholder)"""
    value = get_secret(key)
    if not value:
        return False
    
    # Check if it's a placeholder value
    return not value.startswith('REPLACE_WITH_REAL_') and value != 'sq0atp-REPLACE_WITH_REAL_TOKEN'








