#!/usr/bin/env python3
"""
Google Secret Manager integration for Anytime Fitness Dashboard
Handles secure credential retrieval from Google Cloud Secret Manager
"""

import os
import logging
from typing import Optional
from google.cloud import secretmanager
from google.api_core import exceptions

logger = logging.getLogger(__name__)

class GoogleSecretManager:
    """Google Secret Manager client for secure credential management"""
    
    def __init__(self, project_id: Optional[str] = None):
        """Initialize the Secret Manager client
        
        Args:
            project_id: Google Cloud Project ID. If None, will use GOOGLE_CLOUD_PROJECT env var
        """
        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT')
        if not self.project_id:
            logger.warning("Google Cloud Project ID not found. Set GOOGLE_CLOUD_PROJECT environment variable for production.")
            logger.info("Will fall back to local secrets. Set up GSM for production deployment.")
            # Don't raise error - allow fallback to local secrets during development
            self.client = None
            return
        
        try:
            self.client = secretmanager.SecretManagerServiceClient()
            logger.info(f"✅ Google Secret Manager client initialized for project: {self.project_id}")
        except Exception as e:
            logger.warning(f"❌ Failed to initialize Google Secret Manager client: {e}")
            logger.info("Will fall back to local secrets. Install gcloud CLI and authenticate for GSM access.")
            self.client = None
    
    def get_secret(self, secret_name: str, version: str = "latest") -> Optional[str]:
        """Retrieve a secret from Google Secret Manager
        
        Args:
            secret_name: Name of the secret in GSM
            version: Version of the secret (default: latest)
            
        Returns:
            Secret value as string, or None if not found
        """
        # If GSM client is not available, return None (fallback to local secrets)
        if not self.client or not self.project_id:
            logger.debug(f"GSM not available, returning None for secret: {secret_name}")
            return None
            
        try:
            # Build the resource name
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/{version}"
            
            # Access the secret version
            response = self.client.access_secret_version(request={"name": name})
            
            # Decode the secret payload
            secret_value = response.payload.data.decode("UTF-8")
            
            logger.info(f"✅ Successfully retrieved secret from GSM: {secret_name}")
            return secret_value
            
        except exceptions.NotFound:
            logger.warning(f"⚠️ Secret not found in GSM: {secret_name}")
            return None
        except exceptions.PermissionDenied:
            logger.error(f"❌ Permission denied accessing secret: {secret_name}")
            return None
        except Exception as e:
            logger.error(f"❌ Error retrieving secret {secret_name}: {e}")
            return None
    
    def list_secrets(self) -> list:
        """List all secrets in the project"""
        try:
            parent = f"projects/{self.project_id}"
            secrets = self.client.list_secrets(request={"parent": parent})
            secret_names = [secret.name.split('/')[-1] for secret in secrets]
            logger.info(f"📋 Found {len(secret_names)} secrets in project")
            return secret_names
        except Exception as e:
            logger.error(f"❌ Error listing secrets: {e}")
            return []
    
    def secret_exists(self, secret_name: str) -> bool:
        """Check if a secret exists in GSM"""
        try:
            name = f"projects/{self.project_id}/secrets/{secret_name}"
            self.client.get_secret(request={"name": name})
            return True
        except exceptions.NotFound:
            return False
        except Exception as e:
            logger.error(f"❌ Error checking secret existence {secret_name}: {e}")
            return False

# Global GSM instance (initialized when needed)
_gsm_client = None

def get_gsm_client() -> GoogleSecretManager:
    """Get the global Google Secret Manager client instance"""
    global _gsm_client
    if _gsm_client is None:
        _gsm_client = GoogleSecretManager()
    return _gsm_client

def get_secret_from_gsm(secret_name: str) -> Optional[str]:
    """Convenience function to get a secret from GSM
    
    Args:
        secret_name: Name of the secret
        
    Returns:
        Secret value or None if not found
    """
    try:
        gsm = get_gsm_client()
        return gsm.get_secret(secret_name)
    except Exception as e:
        logger.error(f"❌ Failed to retrieve secret {secret_name} from GSM: {e}")
        return None
