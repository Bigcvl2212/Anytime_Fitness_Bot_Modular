"""
Secure Authentication Service

This service handles manager authentication, session management, and secure credential validation.
"""

import os
import hashlib
import secrets
import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from flask import session, request, current_app

# Import SecureSecretsManager with absolute path handling
try:
    from .secure_secrets_manager import SecureSecretsManager
except ImportError:
    try:
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager
    except ImportError:
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        from secure_secrets_manager import SecureSecretsManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureAuthService:
    """
    Secure authentication service for dashboard managers
    """
    
    def __init__(self, project_id: str = None):
        """
        Initialize the authentication service
        
        Args:
            project_id: GCP project ID for secrets manager
        """
        self.secrets_manager = SecureSecretsManager(project_id)
        self.session_timeout = timedelta(hours=8)  # 8-hour session timeout
        self.clubhub_token = None  # Store ClubHub JWT token
        
    def authenticate_clubhub(self, email: str, password: str) -> Optional[str]:
        """
        Authenticate with ClubHub and get JWT token
        
        Args:
            email: ClubHub email
            password: ClubHub password
            
        Returns:
            JWT token if successful, None otherwise
        """
        try:
            # Import ClubHub client
            import sys, os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))
            from clubhub_api_client import ClubHubAPIClient
            
            client = ClubHubAPIClient()
            
            # Attempt authentication
            if client.authenticate(email, password):
                logger.info("✅ ClubHub authentication successful")
                return client.auth_token
            else:
                logger.warning("❌ ClubHub authentication failed")
                return None
                
        except Exception as e:
            logger.error(f"❌ ClubHub authentication error: {e}")
            return None
        
    def generate_manager_id(self, username: str, email: str) -> str:
        """
        Generate a unique manager ID based on username and email
        
        Args:
            username: ClubOS username
            email: ClubHub email
            
        Returns:
            Unique manager ID
        """
        # Create a deterministic hash of username and email
        combined = f"{username.lower()}:{email.lower()}"
        hash_object = hashlib.sha256(combined.encode())
        return hash_object.hexdigest()[:16]  # Use first 16 characters
    
    def validate_credentials_format(self, clubos_username: str, clubos_password: str,
                                   clubhub_email: str, clubhub_password: str) -> Tuple[bool, str]:
        """
        Validate credential format before storing
        
        Args:
            clubos_username: ClubOS username
            clubos_password: ClubOS password
            clubhub_email: ClubHub email
            clubhub_password: ClubHub password
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not clubos_username or len(clubos_username) < 3:
            return False, "ClubOS username must be at least 3 characters"
        
        if not clubos_password or len(clubos_password) < 8:
            return False, "ClubOS password must be at least 8 characters"
        
        if not clubhub_email or '@' not in clubhub_email:
            return False, "ClubHub email must be a valid email address"
        
        if not clubhub_password or len(clubhub_password) < 8:
            return False, "ClubHub password must be at least 8 characters"
        
        return True, ""
    
    def store_manager_credentials(self, clubos_username: str, clubos_password: str,
                                clubhub_email: str, clubhub_password: str) -> Tuple[bool, str, str]:
        """
        Store manager credentials securely
        
        Args:
            clubos_username: ClubOS username
            clubos_password: ClubOS password
            clubhub_email: ClubHub email
            clubhub_password: ClubHub password
            
        Returns:
            Tuple of (success, manager_id, error_message)
        """
        # Validate format
        is_valid, error_msg = self.validate_credentials_format(
            clubos_username, clubos_password, clubhub_email, clubhub_password
        )
        
        if not is_valid:
            logger.error(f"❌ Invalid credential format: {error_msg}")
            return False, "", error_msg
        
        # Generate manager ID
        manager_id = self.generate_manager_id(clubos_username, clubhub_email)
        
        # Store credentials
        success = self.secrets_manager.store_credentials(
            manager_id=manager_id,
            clubos_username=clubos_username,
            clubos_password=clubos_password,
            clubhub_email=clubhub_email,
            clubhub_password=clubhub_password
        )
        
        if success:
            logger.info(f"✅ Successfully stored credentials for manager {manager_id}")
            return True, manager_id, ""
        else:
            logger.error(f"❌ Failed to store credentials for manager {manager_id}")
            return False, "", "Failed to store credentials securely"
    
    def authenticate_manager(self, clubos_username: str, clubos_password: str,
                           clubhub_email: str, clubhub_password: str) -> Tuple[bool, str, str]:
        """
        Authenticate a manager with their credentials
        
        Args:
            clubos_username: ClubOS username
            clubos_password: ClubOS password
            clubhub_email: ClubHub email
            clubhub_password: ClubHub password
            
        Returns:
            Tuple of (success, manager_id, error_message)
        """
        # Generate manager ID
        manager_id = self.generate_manager_id(clubos_username, clubhub_email)
        
        # Check if credentials exist in Google Secret Manager
        try:
            # Get the expected credentials from Google Secret Manager
            expected_clubos_username = self.secrets_manager.get_secret('clubos-username')
            expected_clubos_password = self.secrets_manager.get_secret('clubos-password')
            expected_clubhub_email = self.secrets_manager.get_secret('clubhub-email')
            expected_clubhub_password = self.secrets_manager.get_secret('clubhub-password')
            
            # If no credentials exist in Secret Manager, this is first-time setup
            if not all([expected_clubos_username, expected_clubos_password, expected_clubhub_email, expected_clubhub_password]):
                logger.info(f"🆕 No credentials found in Secret Manager - attempting first-time setup for manager {manager_id}")
                
                # Test the provided credentials by actually authenticating with ClubHub
                clubhub_token = self.authenticate_clubhub(clubhub_email, clubhub_password)
                if not clubhub_token:
                    logger.warning(f"❌ ClubHub authentication failed during first-time setup for manager {manager_id}")
                    return False, "", "ClubHub authentication failed. Please verify your credentials are correct."
                
                # Store the validated credentials in Secret Manager for future use
                try:
                    self._store_credentials_in_secret_manager(clubos_username, clubos_password, clubhub_email, clubhub_password)
                    logger.info(f"✅ First-time setup complete - credentials stored for manager {manager_id}")
                except Exception as store_error:
                    logger.warning(f"⚠️ Could not store credentials in Secret Manager: {store_error}")
                    # Continue anyway since authentication succeeded
                
                self.clubhub_token = clubhub_token  # Store token for multi-club processing
                return True, manager_id, ""
            
            # Credentials exist in Secret Manager - validate against them
            if (clubos_username == expected_clubos_username and 
                clubos_password == expected_clubos_password and
                clubhub_email == expected_clubhub_email and 
                clubhub_password == expected_clubhub_password):
                
                logger.info(f"✅ Credentials match Google Secret Manager for manager {manager_id}")
                
                # Perform actual ClubHub authentication to get JWT token
                clubhub_token = self.authenticate_clubhub(clubhub_email, clubhub_password)
                if clubhub_token:
                    self.clubhub_token = clubhub_token  # Store token for multi-club processing
                    logger.info(f"✅ Manager {manager_id} authenticated successfully with ClubHub")
                    return True, manager_id, ""
                else:
                    logger.warning(f"❌ ClubHub authentication failed for manager {manager_id}")
                    return False, "", "ClubHub authentication failed"
            else:
                logger.warning(f"❌ Provided credentials do not match Google Secret Manager")
                return False, "", "Invalid credentials. Please check your username and password."
            
        except Exception as e:
            logger.error(f"⚠️ Could not retrieve credentials from Google Secret Manager: {e}")
            return False, "", "Authentication service error. Please try again."
        
        # Note: Removed fallback to local stored credentials since we want everything in the cloud
        
        # Verify credentials match
        if (stored_creds['clubos_username'] == clubos_username and
            stored_creds['clubos_password'] == clubos_password and
            stored_creds['clubhub_email'] == clubhub_email and
            stored_creds['clubhub_password'] == clubhub_password):
            
            # Perform actual ClubHub authentication to get JWT token
            clubhub_token = self.authenticate_clubhub(clubhub_email, clubhub_password)
            if clubhub_token:
                self.clubhub_token = clubhub_token  # Store token for multi-club processing
                logger.info(f"✅ Manager {manager_id} authenticated successfully with ClubHub")
                return True, manager_id, ""
            else:
                logger.warning(f"❌ ClubHub authentication failed for manager {manager_id}")
                return False, "", "ClubHub authentication failed"
        else:
            logger.warning(f"❌ Invalid credentials for manager {manager_id}")
            return False, "", "Invalid credentials"
    
    def create_session(self, manager_id: str) -> str:
        """
        Create a secure session for authenticated manager
        
        Args:
            manager_id: Manager ID
            
        Returns:
            Session token
        """
        session_token = secrets.token_urlsafe(32)
        
        # Store session data in Flask session
        session['authenticated'] = True
        session['manager_id'] = manager_id
        session['session_token'] = session_token
        session['login_time'] = datetime.now().isoformat()
        session['last_activity'] = datetime.now().isoformat()
        
        # Set session to expire
        session.permanent = True
        session.modified = True  # Force Flask to save the session
        current_app.permanent_session_lifetime = self.session_timeout
        
        # Debug: Log session contents after creation
        logger.info(f"✅ Created session for manager {manager_id}")
        logger.info(f"🔍 Session contents after creation: {dict(session)}")
        logger.info(f"🔍 Session.permanent = {session.permanent}")
        
        return session_token
    
    def validate_session(self) -> Tuple[bool, str]:
        """
        Validate the current session
        
        Returns:
            Tuple of (is_valid, manager_id)
        """
        if 'authenticated' not in session or not session['authenticated']:
            return False, ""
        
        if 'manager_id' not in session:
            return False, ""
        
        # Check session timeout
        if 'login_time' in session:
            try:
                login_time = datetime.fromisoformat(session['login_time'])
                if datetime.now() - login_time > self.session_timeout:
                    logger.warning(f"⚠️ Session expired for manager {session.get('manager_id', 'unknown')}")
                    self.logout()
                    return False, ""
            except (ValueError, TypeError):
                logger.error("❌ Invalid session login_time format")
                self.logout()
                return False, ""
        
        # Update last activity
        session['last_activity'] = datetime.now().isoformat()
        
        manager_id = session['manager_id']
        logger.debug(f"✅ Session validated for manager {manager_id}")
        return True, manager_id
    
    def logout(self) -> None:
        """
        Clear the current session
        """
        manager_id = session.get('manager_id', 'unknown')
        
        # Clear all session data
        session.clear()
        
        logger.info(f"✅ Manager {manager_id} logged out")
    
    def get_manager_credentials(self, manager_id: str) -> Optional[Dict[str, str]]:
        """
        Get manager credentials for API calls (only if authenticated)
        
        Args:
            manager_id: Manager ID
            
        Returns:
            Dict with credentials or None
        """
        # Verify session is valid
        is_valid, session_manager_id = self.validate_session()
        
        if not is_valid or session_manager_id != manager_id:
            logger.error(f"❌ Unauthorized attempt to access credentials for {manager_id}")
            return None
        
        return self.secrets_manager.get_credentials(manager_id)
    
    def require_authentication(self):
        """
        Decorator function to require authentication for routes
        
        Returns:
            Decorator function
        """
        def decorator(f):
            def decorated_function(*args, **kwargs):
                is_valid, manager_id = self.validate_session()
                if not is_valid:
                    from flask import redirect, url_for
                    logger.warning(f"❌ Unauthenticated access attempt to {request.endpoint}")
                    return redirect(url_for('login'))
                return f(*args, **kwargs)
            decorated_function.__name__ = f.__name__
            return decorated_function
        return decorator
    
    def get_session_info(self) -> Dict[str, any]:
        """
        Get current session information
        
        Returns:
            Dict with session info
        """
        is_valid, manager_id = self.validate_session()
        
        if not is_valid:
            return {
                'authenticated': False,
                'manager_id': None,
                'login_time': None,
                'last_activity': None
            }
        
        return {
            'authenticated': True,
            'manager_id': manager_id,
            'login_time': session.get('login_time'),
            'last_activity': session.get('last_activity')
        }
    
    def update_manager_credentials(self, manager_id: str, clubos_username: str = None,
                                 clubos_password: str = None, clubhub_email: str = None,
                                 clubhub_password: str = None) -> Tuple[bool, str]:
        """
        Update specific manager credentials
        
        Args:
            manager_id: Manager ID
            clubos_username: New ClubOS username (optional)
            clubos_password: New ClubOS password (optional)
            clubhub_email: New ClubHub email (optional)
            clubhub_password: New ClubHub password (optional)
            
        Returns:
            Tuple of (success, error_message)
        """
        # Verify session
        is_valid, session_manager_id = self.validate_session()
        if not is_valid or session_manager_id != manager_id:
            return False, "Unauthorized"
        
        # Get current credentials
        current_creds = self.secrets_manager.get_credentials(manager_id)
        if not current_creds:
            return False, "Manager credentials not found"
        
        # Update only provided fields
        updated_creds = current_creds.copy()
        if clubos_username is not None:
            updated_creds['clubos_username'] = clubos_username
        if clubos_password is not None:
            updated_creds['clubos_password'] = clubos_password
        if clubhub_email is not None:
            updated_creds['clubhub_email'] = clubhub_email
        if clubhub_password is not None:
            updated_creds['clubhub_password'] = clubhub_password
        
        # Validate updated credentials
        is_valid, error_msg = self.validate_credentials_format(
            updated_creds['clubos_username'],
            updated_creds['clubos_password'],
            updated_creds['clubhub_email'],
            updated_creds['clubhub_password']
        )
        
        if not is_valid:
            return False, error_msg
        
        # Store updated credentials
        success = self.secrets_manager.store_credentials(
            manager_id=manager_id,
            clubos_username=updated_creds['clubos_username'],
            clubos_password=updated_creds['clubos_password'],
            clubhub_email=updated_creds['clubhub_email'],
            clubhub_password=updated_creds['clubhub_password']
        )
        
        if success:
            logger.info(f"✅ Updated credentials for manager {manager_id}")
            return True, ""
        else:
            return False, "Failed to update credentials"
    
    def _store_credentials_in_secret_manager(self, clubos_username: str, clubos_password: str,
                                           clubhub_email: str, clubhub_password: str):
        """Helper method to store individual credentials in Secret Manager"""
        secrets_to_store = {
            'clubos-username': clubos_username,
            'clubos-password': clubos_password,
            'clubhub-email': clubhub_email,
            'clubhub-password': clubhub_password
        }
        
        for secret_name, secret_value in secrets_to_store.items():
            try:
                # Create or update the secret
                parent = f'projects/{self.secrets_manager.project_id}'
                
                # Try to create the secret first
                try:
                    secret = self.secrets_manager.client.create_secret(
                        request={
                            'parent': parent,
                            'secret_id': secret_name,
                            'secret': {'replication': {'automatic': {}}},
                        }
                    )
                    logger.info(f"✅ Created new secret: {secret_name}")
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        logger.info(f"ℹ️ Secret {secret_name} already exists, will update")
                    else:
                        raise e
                
                # Add the secret version
                secret_path = f'projects/{self.secrets_manager.project_id}/secrets/{secret_name}'
                response = self.secrets_manager.client.add_secret_version(
                    request={
                        'parent': secret_path,
                        'payload': {'data': secret_value.encode('UTF-8')},
                    }
                )
                
                logger.info(f"✅ Stored secret: {secret_name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to store secret {secret_name}: {e}")
                raise e