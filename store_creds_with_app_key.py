#!/usr/bin/env python3
"""
Store credentials using the exact same encryption key the app uses
"""
import sys
import os

# Set the FLASK_SECRET_KEY to match what the app uses
os.environ['FLASK_SECRET_KEY'] = 'OdCu_p9fBYb-35AW_ePrRhkRLf6LS-H_MPYeBdOCw_k'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.authentication.secure_secrets_manager import SecureSecretsManager

# Credentials
manager_id = "ef8de92f-f6b5-43"
clubos_username = "j.mayo"
clubos_password = "W-!R6Bv9FgPnuB4"
clubhub_email = "mayo.jeremy2212@gmail.com"
clubhub_password = "fygxy9-sybses-suvtYc"

print("Storing credentials with matching encryption key...")
print(f"Using FLASK_SECRET_KEY from environment")

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
    print(f"\nSUCCESS! Credentials stored for manager_id: {manager_id}")

    # Verify by retrieving them
    print("\nVerifying retrieval...")
    retrieved = secrets_manager.get_credentials(manager_id)
    if retrieved:
        print("VERIFIED! Credentials can be retrieved successfully")
        print(f"  ClubOS Username: {retrieved.get('clubos_username')}")
        print(f"  ClubHub Email: {retrieved.get('clubhub_email')}")
    else:
        print("ERROR: Could not retrieve credentials!")
else:
    print("FAILED to store credentials")
