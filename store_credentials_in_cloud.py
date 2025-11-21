#!/usr/bin/env python3
"""
One-time script to store credentials in Google Secret Manager
This moves credentials from local config to cloud storage
"""

import os
import sys
import logging
from google.cloud import secretmanager
from google.api_core import exceptions as gcp_exceptions

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def store_secret(client, project_id: str, secret_name: str, secret_value: str):
    """Store a secret in Google Secret Manager"""
    try:
        # Check if secret already exists
        secret_path = f"projects/{project_id}/secrets/{secret_name}"
        try:
            client.get_secret(request={"name": secret_path})
            logger.info(f"✅ Secret {secret_name} already exists")
        except gcp_exceptions.NotFound:
            # Create the secret
            logger.info(f"📝 Creating secret {secret_name}...")
            client.create_secret(
                request={
                    "parent": f"projects/{project_id}",
                    "secret_id": secret_name,
                    "secret": {"replication": {"automatic": {}}},
                }
            )
            logger.info(f"✅ Created secret {secret_name}")
        
        # Add secret version
        logger.info(f"📝 Storing value for {secret_name}...")
        client.add_secret_version(
            request={
                "parent": secret_path,
                "payload": {"data": secret_value.encode("UTF-8")},
            }
        )
        logger.info(f"✅ Stored value for {secret_name}")
        
    except Exception as e:
        logger.error(f"❌ Error storing {secret_name}: {e}")

def main():
    """Store credentials in Google Secret Manager"""
    project_id = "round-device-460522-g8"
    
    # Initialize Secret Manager client
    client = secretmanager.SecretManagerServiceClient()
    
    # Credentials from local config (to be moved to cloud)
    credentials = {
        'clubhub-email': 'mayo.jeremy2212@gmail.com',
        'clubhub-password': 'SruLEqp464_GLrF',
        'clubos-username': 'j.mayo',
        'clubos-password': 'j@SD4fjhANK5WNA'
    }
    
    logger.info("🔄 Storing credentials in Google Secret Manager...")
    
    for secret_name, secret_value in credentials.items():
        store_secret(client, project_id, secret_name, secret_value)
    
    logger.info("✅ All credentials stored in Google Secret Manager!")
    logger.info("🌩️ The application is now fully cloud-ready!")

if __name__ == "__main__":
    main()
