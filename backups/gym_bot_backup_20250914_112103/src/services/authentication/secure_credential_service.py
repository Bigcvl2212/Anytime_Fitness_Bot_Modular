"""
Secure Credential Service

This service provides a drop-in replacement for the existing credential access patterns
while using the secure secrets management system.
"""

import os
import logging
from typing import Optional, Dict

# Import with flexible path handling
try:
    from .secure_secrets_manager import SecureSecretsManager
    from .secure_auth_service import SecureAuthService
except ImportError:
    try:
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager
        from src.services.authentication.secure_auth_service import SecureAuthService
    except ImportError:
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        from secure_secrets_manager import SecureSecretsManager
        from secure_auth_service import SecureAuthService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureCredentialService:
    """
    Secure credential service that provides backwards compatibility
    with existing credential access patterns
    """
    
    def __init__(self, project_id: str = None):
        """
        Initialize the secure credential service
        
        Args:
            project_id: GCP project ID
        """
        self.secrets_manager = SecureSecretsManager(project_id)
        self.auth_service = SecureAuthService(project_id)
        
    def get_secret(self, secret_name: str) -> Optional[str]:
        """
        Get secret using the legacy format (backwards compatibility)
        
        This method provides compatibility with existing code that uses:
        from config.secrets_local import get_secret
        
        Args:
            secret_name: Name of the secret
            
        Returns:
            Secret value or None if not found
        """
        return self.secrets_manager.get_legacy_secret(secret_name)
    
    def get_authenticated_credentials(self) -> Optional[Dict[str, str]]:
        """
        Get credentials for the currently authenticated manager
        
        Returns:
            Dict with credentials or None if not authenticated
        """
        try:
            from flask import session
            
            # Check if there's an active session
            if not session.get('authenticated') or not session.get('manager_id'):
                logger.warning("⚠️ No authenticated session found")
                return None
            
            manager_id = session['manager_id']
            
            # Validate session
            is_valid, session_manager_id = self.auth_service.validate_session()
            if not is_valid or session_manager_id != manager_id:
                logger.warning(f"⚠️ Invalid session for manager {manager_id}")
                return None
            
            # Get credentials
            credentials = self.auth_service.get_manager_credentials(manager_id)
            if credentials:
                logger.info(f"✅ Retrieved credentials for authenticated manager {manager_id}")
                return credentials
            else:
                logger.error(f"❌ No credentials found for manager {manager_id}")
                return None
                
        except ImportError:
            logger.warning("⚠️ Flask not available, cannot get authenticated credentials")
            return None
        except Exception as e:
            logger.error(f"❌ Error getting authenticated credentials: {e}")
            return None
    
    def get_clubos_credentials(self) -> tuple:
        """
        Get ClubOS credentials for backwards compatibility
        
        Returns:
            Tuple of (username, password) or (None, None) if not available
        """
        credentials = self.get_authenticated_credentials()
        
        if credentials:
            return credentials.get('clubos_username'), credentials.get('clubos_password')
        
        # Fall back to legacy secrets for backwards compatibility
        username = self.get_secret('clubos-username')
        password = self.get_secret('clubos-password')
        
        if username and password:
            logger.info("ℹ️ Using legacy ClubOS credentials")
            return username, password
        
        logger.warning("⚠️ No ClubOS credentials available")
        return None, None
    
    def get_clubhub_credentials(self) -> tuple:
        """
        Get ClubHub credentials for backwards compatibility
        
        Returns:
            Tuple of (email, password) or (None, None) if not available
        """
        credentials = self.get_authenticated_credentials()
        
        if credentials:
            return credentials.get('clubhub_email'), credentials.get('clubhub_password')
        
        # Fall back to legacy secrets for backwards compatibility
        email = self.get_secret('clubhub-username')  # Some legacy code might use 'username'
        if not email:
            email = self.get_secret('clubhub-email')
        
        password = self.get_secret('clubhub-password')
        
        if email and password:
            logger.info("ℹ️ Using legacy ClubHub credentials")
            return email, password
        
        logger.warning("⚠️ No ClubHub credentials available")
        return None, None

# Global instance for backwards compatibility
_credential_service = None

def get_secure_credential_service() -> SecureCredentialService:
    """
    Get the global secure credential service instance
    
    Returns:
        SecureCredentialService instance
    """
    global _credential_service
    if _credential_service is None:
        _credential_service = SecureCredentialService()
    return _credential_service

def get_secret(secret_name: str) -> Optional[str]:
    """
    Backwards compatible get_secret function
    
    This function can be used as a drop-in replacement for the existing get_secret function
    
    Args:
        secret_name: Name of the secret
        
    Returns:
        Secret value or None if not found
    """
    service = get_secure_credential_service()
    return service.get_secret(secret_name)

def get_clubos_credentials() -> tuple:
    """
    Get ClubOS credentials
    
    Returns:
        Tuple of (username, password) or (None, None) if not available
    """
    service = get_secure_credential_service()
    return service.get_clubos_credentials()

def get_clubhub_credentials() -> tuple:
    """
    Get ClubHub credentials
    
    Returns:
        Tuple of (email, password) or (None, None) if not available
    """
    service = get_secure_credential_service()
    return service.get_clubhub_credentials()

def is_authenticated() -> bool:
    """
    Check if there's an authenticated session
    
    Returns:
        True if authenticated, False otherwise
    """
    try:
        from flask import session
        return session.get('authenticated', False)
    except ImportError:
        return False

def get_current_manager_id() -> Optional[str]:
    """
    Get the current authenticated manager ID
    
    Returns:
        Manager ID or None if not authenticated
    """
    try:
        from flask import session
        if session.get('authenticated'):
            return session.get('manager_id')
        return None
    except ImportError:
        return None