#!/usr/bin/env python3
"""
Test retrieving credentials
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.authentication.secure_secrets_manager import SecureSecretsManager

manager_id = "ef8de92f-f6b5-43"

print(f"Testing credential retrieval for manager_id: {manager_id}")

secrets_manager = SecureSecretsManager()
credentials = secrets_manager.get_credentials(manager_id)

print(f"\nResult: {credentials}")

if credentials:
    print("\nCredentials retrieved successfully:")
    print(f"  ClubOS Username: {credentials.get('clubos_username')}")
    print(f"  ClubOS Password: {'*' * len(credentials.get('clubos_password', ''))}")
    print(f"  ClubHub Email: {credentials.get('clubhub_email')}")
    print(f"  ClubHub Password: {'*' * len(credentials.get('clubhub_password', ''))}")
else:
    print("\nFAILED: No credentials retrieved")
