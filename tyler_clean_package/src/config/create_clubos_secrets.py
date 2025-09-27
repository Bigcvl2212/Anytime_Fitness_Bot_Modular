#!/usr/bin/env python3
"""
Create ClubOS Secrets in Google Secret Manager
Run this once to set up the missing secrets for production
"""

import os
import sys
from google.cloud import secretmanager

def create_clubos_secrets():
    """Create the missing ClubOS secrets in Google Secret Manager."""
    
    project_id = "round-device-460522-g8"
    client = secretmanager.SecretManagerServiceClient()
    
    # Secrets to create (you'll need to provide the actual values)
    secrets_to_create = {
        "clubos-username": {
            "description": "ClubOS portal username for API access",
            "value": ""  # Replace with actual ClubOS username
        },
        "clubos-password": {
            "description": "ClubOS portal password for API access", 
            "value": ""  # Replace with actual ClubOS password
        }
    }
    
    for secret_id, config in secrets_to_create.items():
        try:
            # Check if secret already exists
            secret_name = f"projects/{project_id}/secrets/{secret_id}"
            try:
                client.get_secret(request={"name": secret_name})
                print(f"✅ Secret {secret_id} already exists")
                continue
            except Exception:
                pass  # Secret doesn't exist, create it
            
            # Create the secret
            parent = f"projects/{project_id}"
            secret = client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": {
                        "labels": {"environment": "production", "service": "gym-bot"},
                        "replication": {"automatic": {}}
                    }
                }
            )
            print(f"✅ Created secret: {secret.name}")
            
            # Add secret version (only if value is provided)
            if config["value"]:
                client.add_secret_version(
                    request={
                        "parent": secret.name,
                        "payload": {"data": config["value"].encode("UTF-8")}
                    }
                )
                print(f"✅ Added version to secret {secret_id}")
            else:
                print(f"⚠️ Secret {secret_id} created but no value provided. Add manually.")
                
        except Exception as e:
            print(f"❌ Error creating secret {secret_id}: {e}")

if __name__ == "__main__":
    print("🔧 Creating ClubOS secrets in Google Secret Manager...")
    print("⚠️ You need to manually add the actual credentials to this script")
    print("⚠️ Or create the secrets manually in Google Cloud Console")
    
    # Uncomment the line below after adding credentials
    # create_clubos_secrets()
    
    print("\n📋 Manual steps to complete:")
    print("1. Go to Google Cloud Console > Secret Manager")
    print("2. Create secrets: clubos-username, clubos-password")
    print("3. Add the actual ClubOS portal credentials")
    print("4. Ensure the Cloud Run service account has access")