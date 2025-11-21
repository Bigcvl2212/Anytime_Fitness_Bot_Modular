#!/usr/bin/env python3
"""
Store ClubHub credentials properly using SecureSecretsManager
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.authentication.secure_secrets_manager import SecureSecretsManager

# Credentials
manager_id = "ef8de92f-f6b5-43"
clubos_username = "j.mayo"
clubos_password = "W-!R6Bv9FgPnuB4"
clubhub_email = "mayo.jeremy2212@gmail.com"
clubhub_password = "fygxy9-sybses-suvtYc"

print("Storing credentials using SecureSecretsManager...")

# Use the proper secrets manager
secrets_manager = SecureSecretsManager()

success = secrets_manager.store_credentials(
    manager_id=manager_id,
    clubos_username=clubos_username,
    clubos_password=clubos_password,
    clubhub_email=clubhub_email,
    clubhub_password=clubhub_password
)

if success:
    print(f"SUCCESS! Credentials stored for manager_id: {manager_id}")
    print(f"  ClubOS Username: {clubos_username}")
    print(f"  ClubHub Email: {clubhub_email}")
    print("\nYou can now log in and your clubs will be loaded from ClubHub!")
else:
    print("FAILED to store credentials")
