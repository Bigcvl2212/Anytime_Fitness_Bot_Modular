"""
Secure Secrets Management Service

This service provides secure storage and retrieval of credentials using Google Secret Manager.
It replaces hardcoded credentials with cloud-based secret storage.
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from google.cloud import secretmanager
from google.api_core import exceptions as gcp_exceptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureSecretsManager:
    """
    Secure secrets management using Google Cloud Secret Manager
    """
    
    def __init__(self, project_id: str = None):
        """
        Initialize the secrets manager
        
        Args:
            project_id: GCP project ID. If None, will try to get from environment
        """
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID', 'round-device-460522-g8')
        
        try:
            self.client = secretmanager.SecretManagerServiceClient()
            logger.info("✅ SecretManager client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize SecretManager client: {e}")
            self.client = None
    
    def store_credentials(self, manager_id: str, clubos_username: str, clubos_password: str, 
                         clubhub_email: str, clubhub_password: str) -> bool:
        """
        Securely store manager credentials in Google Secret Manager
        
        Args:
            manager_id: Unique identifier for the manager
            clubos_username: ClubOS username
            clubos_password: ClubOS password
            clubhub_email: ClubHub email
            clubhub_password: ClubHub password
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            logger.error("❌ SecretManager client not initialized")
            return False
        
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
            
            logger.info(f"✅ Stored credentials for manager {manager_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store credentials for manager {manager_id}: {e}")
            return False
    
    def get_credentials(self, manager_id: str) -> Optional[Dict[str, str]]:
        """
        Retrieve manager credentials from Google Secret Manager
        
        Args:
            manager_id: Unique identifier for the manager
            
        Returns:
            Dict with credentials or None if not found
        """
        if not self.client:
            logger.error("❌ SecretManager client not initialized")
            return None
        
        try:
            secret_id = f"manager-credentials-{manager_id}"
            secret_path = f"projects/{self.project_id}/secrets/{secret_id}/versions/latest"
            
            response = self.client.access_secret_version(request={"name": secret_path})
            secret_value = response.payload.data.decode("UTF-8")
            
            credentials = json.loads(secret_value)
            logger.info(f"✅ Retrieved credentials for manager {manager_id}")
            
            return credentials
            
        except gcp_exceptions.NotFound:
            logger.warning(f"⚠️ Credentials not found for manager {manager_id}")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to retrieve credentials for manager {manager_id}: {e}")
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
        if not self.client:
            logger.error("❌ SecretManager client not initialized")
            return None
        
        try:
            # First try environment variables (for local development)
            env_var_name = secret_name.upper().replace('-', '_')
            env_value = os.environ.get(env_var_name)
            if env_value:
                logger.info(f"ℹ️ Using environment variable for {secret_name}")
                return env_value
            
            # Fall back to Secret Manager
            secret_path = f"projects/{self.project_id}/secrets/{secret_name}/versions/{version}"
            response = self.client.access_secret_version(request={"name": secret_path})
            return response.payload.data.decode("UTF-8")
            
        except gcp_exceptions.NotFound:
            logger.warning(f"⚠️ Legacy secret not found: {secret_name}")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get legacy secret {secret_name}: {e}")
            return None
    
    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """
        Create or update a secret in Google Secret Manager
        
        Args:
            secret_name: Name of the secret
            secret_value: Value to store
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("❌ SecretManager client not initialized")
            return False
        
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
                return True
                
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
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to set secret {secret_name}: {e}")
            return False

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