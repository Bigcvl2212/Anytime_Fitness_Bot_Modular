#!/usr/bin/env python3

import os
import sys
import json
sys.path.append('src')

from src.config.environment_setup import load_environment_variables
load_environment_variables()

from src.services.authentication.secure_secrets_manager import SecureSecretsManager

def create_database_secret():
    """Create database-config secret in Google Secret Manager"""
    print("🔐 Creating database-config secret in Google Secret Manager...")
    
    # Get database config from environment variables
    db_config = {
        "host": os.environ.get('DB_HOST', '34.31.91.96'),
        "port": os.environ.get('DB_PORT', '5432'),
        "database": os.environ.get('DB_NAME', 'gym_bot'),
        "username": os.environ.get('DB_USER', 'postgres'),
        "password": os.environ.get('DB_PASSWORD', 'GymBot2025!')
    }
    
    print("📋 Database configuration to store:")
    for key, value in db_config.items():
        if key == 'password':
            print(f"  {key}: {'*' * len(value)}")
        else:
            print(f"  {key}: {value}")
    
    # Convert to JSON
    db_config_json = json.dumps(db_config, indent=2)
    
    # Store in Secret Manager
    secrets_manager = SecureSecretsManager()
    success = secrets_manager.set_secret('database-config', db_config_json)
    
    if success:
        print("✅ Successfully created database-config secret in Google Secret Manager!")
        
        # Test retrieving it
        print("\n🔍 Testing secret retrieval...")
        retrieved_config = secrets_manager.get_secret('database-config')
        if retrieved_config:
            try:
                parsed_config = json.loads(retrieved_config)
                print("✅ Secret retrieval successful:")
                for key, value in parsed_config.items():
                    if key == 'password':
                        print(f"  {key}: {'*' * len(value)}")
                    else:
                        print(f"  {key}: {value}")
                return True
            except json.JSONDecodeError:
                print("❌ Retrieved secret is not valid JSON")
                return False
        else:
            print("❌ Failed to retrieve secret")
            return False
    else:
        print("❌ Failed to create database-config secret")
        return False

if __name__ == "__main__":
    success = create_database_secret()
    sys.exit(0 if success else 1)