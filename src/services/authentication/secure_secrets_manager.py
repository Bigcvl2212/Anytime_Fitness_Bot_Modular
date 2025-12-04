"""
Secure Secrets Management Service

This service provides secure storage and retrieval of credentials.
Primarily uses local database/environment variables.
Google Secret Manager support is optional and only used if explicitly configured.
"""

import os
import json
import logging
from typing import Dict, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Google Cloud dependencies - optional for local/build environments
try:
    from google.cloud import secretmanager
    from google.api_core import exceptions as gcp_exceptions
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    secretmanager = None
    gcp_exceptions = None
    GOOGLE_CLOUD_AVAILABLE = False
    # Only log at debug level - this is expected for local installations
    logger.debug("Google Cloud SDK not installed - using local credentials (this is normal)")

class SecureSecretsManager:
    """
    Secure secrets management - prioritizes local storage (database + environment variables)
    Google Cloud Secret Manager is optional and only used for cloud deployments.
    """
    
    def __init__(self, project_id: str = None):
        """
        Initialize the secrets manager
        
        Args:
            project_id: GCP project ID (optional, only needed for cloud deployments)
        """
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID')
        self.client = None
        
        # Only try to initialize GCP client if we have a project ID and libs available
        if GOOGLE_CLOUD_AVAILABLE and self.project_id:
            try:
                self.client = secretmanager.SecretManagerServiceClient()
                logger.debug("SecretManager client initialized (cloud mode)")
            except Exception as e:
                logger.debug(f"GCP SecretManager not available: {e} - using local mode")
                self.client = None
        else:
            logger.debug("Using local credentials mode (no GCP)")
    
    def store_credentials(self, manager_id: str, clubos_username: str, clubos_password: str,
                         clubhub_email: str, clubhub_password: str) -> bool:
        """
        Securely store manager credentials in database and/or Google Secret Manager

        Args:
            manager_id: Unique identifier for the manager
            clubos_username: ClubOS username
            clubos_password: ClubOS password
            clubhub_email: ClubHub email
            clubhub_password: ClubHub password

        Returns:
            bool: True if successful, False otherwise
        """
        # Try to store in database first (always works locally)
        db_success = False
        try:
            from ..database_manager import DatabaseManager
            from cryptography.fernet import Fernet
            import base64
            import hashlib

            db = DatabaseManager()

            # Create table if not exists
            with db.get_cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS manager_credentials (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        manager_id TEXT UNIQUE NOT NULL,
                        clubos_username TEXT,
                        clubos_password TEXT,
                        clubhub_email TEXT,
                        clubhub_password TEXT,
                        square_access_token TEXT,
                        square_location_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Encrypt credentials
                secret_key = os.getenv('FLASK_SECRET_KEY', 'OdCu_p9fBYb-35AW_ePrRhkRLf6LS-H_MPYeBdOCw_k')
                key = base64.urlsafe_b64encode(hashlib.sha256(secret_key.encode()).digest())
                cipher = Fernet(key)

                encrypted_clubos_username = cipher.encrypt(clubos_username.encode()).decode()
                encrypted_clubos_password = cipher.encrypt(clubos_password.encode()).decode()
                encrypted_clubhub_email = cipher.encrypt(clubhub_email.encode()).decode()
                encrypted_clubhub_password = cipher.encrypt(clubhub_password.encode()).decode()

                # Insert or update
                cursor.execute('''
                    INSERT OR REPLACE INTO manager_credentials
                    (manager_id, clubos_username, clubos_password, clubhub_email, clubhub_password, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    manager_id,
                    encrypted_clubos_username,
                    encrypted_clubos_password,
                    encrypted_clubhub_email,
                    encrypted_clubhub_password
                ))

                cursor.connection.commit()

            logger.info(f"✅ Stored credentials in database for manager {manager_id}")
            db_success = True

        except Exception as db_error:
            logger.error(f"❌ Failed to store credentials in database: {db_error}")

        # Try to store in Google Secret Manager (if available)
        gcp_success = False
        if self.client:
            try:
                # Create credentials object
                credentials_data = {
                    "clubos_username": clubos_username,
                    "clubos_password": clubos_password,
                    "clubhub_email": clubhub_email,
                    "clubhub_password": clubhub_password,
                    "manager_id": manager_id
                }

                # Store credentials as JSON in secret
                secret_id = f"manager-credentials-{manager_id}"
                secret_value = json.dumps(credentials_data)

                # Create or update the secret
                parent = f"projects/{self.project_id}"

                try:
                    # Try to create the secret first
                    secret = self.client.create_secret(
                        request={
                            "parent": parent,
                            "secret_id": secret_id,
                            "secret": {"replication": {"automatic": {}}},
                        }
                    )
                    logger.info(f"✅ Created new secret: {secret_id}")
                except gcp_exceptions.AlreadyExists:
                    # Secret already exists, that's fine
                    logger.info(f"ℹ️ Secret {secret_id} already exists, will update")

                # Add the secret version
                secret_path = f"projects/{self.project_id}/secrets/{secret_id}"
                response = self.client.add_secret_version(
                    request={
                        "parent": secret_path,
                        "payload": {"data": secret_value.encode("UTF-8")},
                    }
                )

                logger.info(f"✅ Stored credentials in Google Secret Manager for manager {manager_id}")
                gcp_success = True

            except Exception as e:
                logger.debug(f"Google Secret Manager storage failed: {e}")

        # Success if either storage method worked
        return db_success or gcp_success
    
    def get_credentials(self, manager_id: str) -> Optional[Dict[str, str]]:
        """
        Retrieve manager credentials from database or Google Secret Manager

        Args:
            manager_id: Unique identifier for the manager

        Returns:
            Dict with credentials or None if not found
        """
        # Try database first (local storage)
        try:
            from ..database_manager import DatabaseManager
            from cryptography.fernet import Fernet
            import base64
            import hashlib

            db = DatabaseManager()

            with db.get_cursor() as cursor:
                cursor.execute('''
                    SELECT clubos_username, clubos_password, clubhub_email, clubhub_password
                    FROM manager_credentials
                    WHERE manager_id = ?
                ''', (manager_id,))

                row = cursor.fetchone()

                if row:
                    # Decrypt credentials
                    secret_key = os.getenv('FLASK_SECRET_KEY', 'OdCu_p9fBYb-35AW_ePrRhkRLf6LS-H_MPYeBdOCw_k')
                    key = base64.urlsafe_b64encode(hashlib.sha256(secret_key.encode()).digest())
                    cipher = Fernet(key)

                    credentials = {
                        'clubos_username': cipher.decrypt(row[0].encode()).decode() if row[0] else None,
                        'clubos_password': cipher.decrypt(row[1].encode()).decode() if row[1] else None,
                        'clubhub_email': cipher.decrypt(row[2].encode()).decode() if row[2] else None,
                        'clubhub_password': cipher.decrypt(row[3].encode()).decode() if row[3] else None,
                    }

                    logger.info(f"✅ Retrieved credentials from database for manager {manager_id}")
                    return credentials
                else:
                    logger.warning(f"⚠️ No credentials found in database for manager {manager_id}")
        except Exception as db_error:
            logger.error(f"❌ Database credentials retrieval failed: {db_error}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")

        # Fallback to Google Secret Manager (but only if database failed)
        if not self.client:
            logger.debug("SecretManager client not initialized, only database storage available")
            return None

        try:
            secret_id = f"manager-credentials-{manager_id}"
            secret_path = f"projects/{self.project_id}/secrets/{secret_id}/versions/latest"

            response = self.client.access_secret_version(request={"name": secret_path})
            secret_value = response.payload.data.decode("UTF-8")

            credentials = json.loads(secret_value)
            logger.info(f"✅ Retrieved credentials from Google Secret Manager for manager {manager_id}")

            return credentials

        except gcp_exceptions.NotFound:
            logger.debug(f"Credentials not found in Google Secret Manager for manager {manager_id}")
            return None
        except gcp_exceptions.PermissionDenied:
            logger.debug(f"Google Secret Manager access denied (billing disabled)")
            return None
        except Exception as e:
            logger.debug(f"Google Secret Manager retrieval failed: {e}")
            return None
    
    def delete_credentials(self, manager_id: str) -> bool:
        """
        Delete manager credentials from Google Secret Manager
        
        Args:
            manager_id: Unique identifier for the manager
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            logger.error("❌ SecretManager client not initialized")
            return False
        
        try:
            secret_id = f"manager-credentials-{manager_id}"
            secret_path = f"projects/{self.project_id}/secrets/{secret_id}"
            
            self.client.delete_secret(request={"name": secret_path})
            logger.info(f"✅ Deleted credentials for manager {manager_id}")
            return True
            
        except gcp_exceptions.NotFound:
            logger.warning(f"⚠️ Credentials not found for manager {manager_id}")
            return True  # Already deleted
        except Exception as e:
            logger.error(f"❌ Failed to delete credentials for manager {manager_id}: {e}")
            return False
    
    def list_managers(self) -> list:
        """
        List all managers with stored credentials
        
        Returns:
            List of manager IDs
        """
        if not self.client:
            logger.error("❌ SecretManager client not initialized")
            return []
        
        try:
            parent = f"projects/{self.project_id}"
            secrets = self.client.list_secrets(request={"parent": parent})
            
            managers = []
            for secret in secrets:
                secret_name = secret.name.split('/')[-1]
                if secret_name.startswith('manager-credentials-'):
                    manager_id = secret_name.replace('manager-credentials-', '')
                    managers.append(manager_id)
            
            logger.info(f"✅ Found {len(managers)} managers with stored credentials")
            return managers
            
        except Exception as e:
            logger.error(f"❌ Failed to list managers: {e}")
            return []
    
    def validate_credentials(self, manager_id: str) -> bool:
        """
        Validate that credentials exist and are properly formatted
        
        Args:
            manager_id: Unique identifier for the manager
            
        Returns:
            bool: True if valid, False otherwise
        """
        credentials = self.get_credentials(manager_id)
        
        if not credentials:
            return False
        
        required_fields = ['clubos_username', 'clubos_password', 'clubhub_email', 'clubhub_password']
        
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                logger.error(f"❌ Invalid credentials for manager {manager_id}: missing {field}")
                return False
        
        logger.info(f"✅ Credentials validated for manager {manager_id}")
        return True

    def get_secret(self, secret_name: str, version: str = "latest") -> Optional[str]:
        """
        Get secret from Google Secret Manager
        
        Args:
            secret_name: Name of the secret
            version: Version to retrieve
            
        Returns:
            Secret value or None if not found
        """
        return self.get_legacy_secret(secret_name, version)
    
    def get_legacy_secret(self, secret_name: str, version: str = "latest") -> Optional[str]:
        """
        Get secret using the legacy format (for backwards compatibility)

        Args:
            secret_name: Name of the secret
            version: Version to retrieve

        Returns:
            Secret value or None if not found
        """
        # ALWAYS try environment variables first (for local development)
        env_var_name = secret_name.upper().replace('-', '_')
        env_value = os.environ.get(env_var_name)

        # Check if env value is a placeholder
        placeholder_values = [
            'your_clubos_username_here',
            'your_clubos_password_here',
            'your_clubhub_email_here',
            'your_clubhub_password_here',
            'your-clubhub-email@example.com',
            'your_square_access_token_here',
            'your_square_location_id_here',
            'replace_me',
            'change_me'
        ]

        if env_value:
            # Don't use placeholder values
            if any(placeholder.lower() in env_value.lower() for placeholder in placeholder_values):
                logger.warning(f"⚠️ Placeholder value detected for {secret_name}, skipping")
                env_value = None
            else:
                logger.info(f"ℹ️ Using environment variable for {secret_name}")
                return env_value

        # Try database for Square credentials (format: square-access-token-{manager_id})
        if 'square-access-token-' in secret_name or 'square-location-id-' in secret_name:
            try:
                from ..database_manager import DatabaseManager
                from cryptography.fernet import Fernet
                import base64
                import hashlib

                # Extract manager_id from secret name
                if 'square-access-token-' in secret_name:
                    manager_id = secret_name.replace('square-access-token-', '')
                    field = 'square_access_token'
                else:
                    manager_id = secret_name.replace('square-location-id-', '')
                    field = 'square_location_id'

                db = DatabaseManager()

                with db.get_cursor() as cursor:
                    cursor.execute(f'''
                        SELECT {field}
                        FROM manager_credentials
                        WHERE manager_id = ?
                    ''', (manager_id,))

                    row = cursor.fetchone()

                    if row and row[0]:
                        # Decrypt
                        secret_key = os.getenv('FLASK_SECRET_KEY', 'OdCu_p9fBYb-35AW_ePrRhkRLf6LS-H_MPYeBdOCw_k')
                        key = base64.urlsafe_b64encode(hashlib.sha256(secret_key.encode()).digest())
                        cipher = Fernet(key)

                        decrypted = cipher.decrypt(row[0].encode()).decode()
                        logger.info(f"✅ Retrieved {field} from database for {manager_id}")
                        return decrypted
            except Exception as db_error:
                logger.debug(f"Database Square credential retrieval failed: {db_error}")

        # Try secrets_local.py as a fallback (for local development)
        try:
            import sys
            import os as os_module

            # Add config directory to path
            config_path = os_module.path.join(os_module.path.dirname(__file__), '..', '..', '..', 'config')
            if config_path not in sys.path:
                sys.path.insert(0, config_path)

            from secrets_local import get_secret as get_local_secret
            local_value = get_local_secret(secret_name)
            if local_value:
                logger.info(f"✅ Retrieved {secret_name} from secrets_local.py")
                return local_value
        except ImportError:
            logger.debug(f"secrets_local.py not available for {secret_name}")
        except Exception as e:
            logger.debug(f"Failed to get secret from secrets_local.py: {e}")

        # Only try Secret Manager if client is initialized
        if not self.client:
            logger.debug(f"SecretManager client not initialized, no alternative source for {secret_name}")
            return None

        try:
            # Fall back to Secret Manager
            secret_path = f"projects/{self.project_id}/secrets/{secret_name}/versions/{version}"
            response = self.client.access_secret_version(request={"name": secret_path})
            return response.payload.data.decode("UTF-8")

        except gcp_exceptions.NotFound:
            logger.warning(f"⚠️ Legacy secret not found: {secret_name}")
            return None
        except gcp_exceptions.PermissionDenied:
            logger.debug(f"Secret Manager access denied for {secret_name} (billing may be disabled)")
            return None
        except Exception as e:
            logger.debug(f"Failed to get secret {secret_name} from Secret Manager: {e}")
            return None
    
    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """
        Create or update a secret in database and/or Google Secret Manager

        Args:
            secret_name: Name of the secret
            secret_value: Value to store

        Returns:
            True if successful, False otherwise
        """
        # Try to store Square credentials in database first
        db_success = False
        if 'square-access-token-' in secret_name or 'square-location-id-' in secret_name:
            try:
                from ..database_manager import DatabaseManager
                from cryptography.fernet import Fernet
                import base64
                import hashlib

                # Extract manager_id from secret name
                if 'square-access-token-' in secret_name:
                    manager_id = secret_name.replace('square-access-token-', '')
                    field = 'square_access_token'
                else:
                    manager_id = secret_name.replace('square-location-id-', '')
                    field = 'square_location_id'

                db = DatabaseManager()

                # Encrypt value
                secret_key = os.getenv('FLASK_SECRET_KEY', 'OdCu_p9fBYb-35AW_ePrRhkRLf6LS-H_MPYeBdOCw_k')
                key = base64.urlsafe_b64encode(hashlib.sha256(secret_key.encode()).digest())
                cipher = Fernet(key)

                encrypted_value = cipher.encrypt(secret_value.encode()).decode()

                # Update database
                with db.get_cursor() as cursor:
                    # Create table if not exists
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS manager_credentials (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            manager_id TEXT UNIQUE NOT NULL,
                            clubos_username TEXT,
                            clubos_password TEXT,
                            clubhub_email TEXT,
                            clubhub_password TEXT,
                            square_access_token TEXT,
                            square_location_id TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')

                    # Check if row exists
                    cursor.execute('SELECT id FROM manager_credentials WHERE manager_id = ?', (manager_id,))
                    exists = cursor.fetchone()

                    if exists:
                        # Update existing row
                        cursor.execute(f'''
                            UPDATE manager_credentials
                            SET {field} = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE manager_id = ?
                        ''', (encrypted_value, manager_id))
                    else:
                        # Insert new row
                        cursor.execute(f'''
                            INSERT INTO manager_credentials (manager_id, {field}, updated_at)
                            VALUES (?, ?, CURRENT_TIMESTAMP)
                        ''', (manager_id, encrypted_value))

                    cursor.connection.commit()

                logger.info(f"✅ Stored {field} in database for manager {manager_id}")
                db_success = True

            except Exception as db_error:
                logger.debug(f"Database storage failed for {secret_name}: {db_error}")

        # Try Google Secret Manager (if available)
        gcp_success = False
        if self.client:
            try:
                # Check if secret exists
                secret_path = f"projects/{self.project_id}/secrets/{secret_name}"

                try:
                    # Try to get the secret to see if it exists
                    self.client.get_secret(request={"name": secret_path})
                    logger.info(f"📝 Updating existing secret: {secret_name}")

                    # Add a new version to the existing secret
                    parent = secret_path
                    payload = {"data": secret_value.encode("UTF-8")}
                    response = self.client.add_secret_version(
                        request={"parent": parent, "payload": payload}
                    )
                    logger.info(f"✅ Successfully updated secret: {secret_name}")
                    gcp_success = True

                except gcp_exceptions.NotFound:
                    # Secret doesn't exist, create it
                    logger.info(f"🆕 Creating new secret: {secret_name}")

                    # Create the secret
                    parent = f"projects/{self.project_id}"
                    secret = {
                        "replication": {"automatic": {}}
                    }
                    self.client.create_secret(
                        request={"parent": parent, "secret_id": secret_name, "secret": secret}
                    )

                    # Add the secret value
                    payload = {"data": secret_value.encode("UTF-8")}
                    response = self.client.add_secret_version(
                        request={"parent": secret_path, "payload": payload}
                    )
                    logger.info(f"✅ Successfully created secret: {secret_name}")
                    gcp_success = True

            except Exception as e:
                logger.debug(f"Google Secret Manager storage failed for {secret_name}: {e}")

        # Success if either storage method worked (or if it's not a Square credential)
        if 'square-' in secret_name:
            return db_success or gcp_success
        else:
            # For non-Square secrets, only GCP is supported currently
            return gcp_success if self.client else False

    def store_session_data(self, session_token: str, session_data: dict) -> bool:
        """
        Store session data in Google Secret Manager

        Args:
            session_token: The session token as key
            session_data: Dictionary containing session data

        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            secret_name = f"session-{session_token}"
            json_data = json.dumps(session_data)
            return self.set_secret(secret_name, json_data)
        except Exception as e:
            logger.error(f"❌ Failed to store session data: {e}")
            return False

    def get_session_data(self, session_token: str) -> dict:
        """
        Retrieve session data from Google Secret Manager

        Args:
            session_token: The session token

        Returns:
            Dictionary containing session data or None if not found
        """
        try:
            import json
            secret_name = f"session-{session_token}"
            json_data = self.get_secret(secret_name)
            if json_data:
                return json.loads(json_data)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get session data: {e}")
            return None

    def delete_session_data(self, session_token: str) -> bool:
        """
        Delete session data from Google Secret Manager

        Args:
            session_token: The session token

        Returns:
            True if successful, False otherwise
        """
        try:
            secret_name = f"session-{session_token}"
            secret_path = f"projects/{self.project_id}/secrets/{secret_name}"
            self.client.delete_secret(request={"name": secret_path})
            logger.info(f"✅ Deleted session data: {secret_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete session data: {e}")
            return False