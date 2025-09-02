"""
Authentication services package
"""

from .secure_secrets_manager import SecureSecretsManager
from .secure_auth_service import SecureAuthService
from .secure_credential_service import (
    SecureCredentialService,
    get_secret,
    get_clubos_credentials,
    get_clubhub_credentials,
    is_authenticated,
    get_current_manager_id
)

__all__ = [
    'SecureSecretsManager',
    'SecureAuthService', 
    'SecureCredentialService',
    'get_secret',
    'get_clubos_credentials',
    'get_clubhub_credentials',
    'is_authenticated',
    'get_current_manager_id'
]