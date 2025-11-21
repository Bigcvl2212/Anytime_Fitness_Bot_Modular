#!/usr/bin/env python3
"""
Store credentials with the EXACT key the app uses
"""
import sys
import os

# Use the EXACT key from the running app
os.environ['FLASK_SECRET_KEY'] = '8CjA9r9dxVjMkhONTOQuSWoPRJPquoatLY9Hz5wVm_M'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.authentication.secure_secrets_manager import SecureSecretsManager

manager_id = "ef8de92f-f6b5-43"
clubos_username = "j.mayo"
clubos_password = "W-!R6Bv9FgPnuB4"
clubhub_email = "mayo.jeremy2212@gmail.com"
clubhub_password = "fygxy9-sybses-suvtYc"

print(f"Storing credentials with CORRECT app key: 8CjA9r9d...")

secrets_manager = SecureSecretsManager()
success = secrets_manager.store_credentials(
    manager_id=manager_id,
    clubos_username=clubos_username,
    clubos_password=clubos_password,
    clubhub_email=clubhub_email,
    clubhub_password=clubhub_password
)

if success:
    print(f"SUCCESS! Now verifying...")
    retrieved = secrets_manager.get_credentials(manager_id)
    if retrieved:
        print("VERIFIED! Credentials work!")
        print(f"ClubOS: {retrieved.get('clubos_username')}")
        print(f"ClubHub: {retrieved.get('clubhub_email')}")
    else:
        print("FAILED verification")
else:
    print("FAILED to store")
