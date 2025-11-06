#!/usr/bin/env python3
"""
Test that address field mapping works correctly
"""
import sys
sys.path.insert(0, '.')

from src.services.api.clubhub_api_client import ClubHubAPIClient
from src.services.authentication.secure_secrets_manager import SecureSecretsManager
from src.services.database_manager import DatabaseManager
import os

# Set up environment
os.environ['FLASK_SECRET_KEY'] = '8CjA9r9dxVjMkhONTOQuSWoPRJPquoatLY9Hz5wVm_M'

# Get credentials
secrets_manager = SecureSecretsManager()
creds = secrets_manager.get_credentials('ef8de92f-f6b5-43')

clubhub_email = creds.get('clubhub_email') if creds else None
clubhub_password = creds.get('clubhub_password') if creds else None

if not clubhub_email or not clubhub_password:
    print("ERROR: No credentials found")
    sys.exit(1)

# Authenticate with ClubHub
client = ClubHubAPIClient()
client.club_id = '1156'

if not client.authenticate(clubhub_email, clubhub_password):
    print("ERROR: Authentication failed")
    sys.exit(1)

print("OK - Authenticated with ClubHub")

# Get just 1 member to test
print("\nFetching 1 member from ClubHub...")
response = client.get_all_members(page=1, page_size=1, club_id='1156')

if not response:
    print("ERROR: No response from ClubHub")
    sys.exit(1)

members = response if isinstance(response, list) else response.get('members', [])

if not members:
    print("ERROR: No members returned")
    sys.exit(1)

member = members[0]
print(f"\nSample member from ClubHub API:")
print(f"  Name: {member.get('firstName')} {member.get('lastName')}")
print(f"  address1: {member.get('address1')}")
print(f"  address2: {member.get('address2')}")
print(f"  city: {member.get('city')}")
print(f"  state: {member.get('state')}")
print(f"  zip: {member.get('zip')}")

# Add full_name for database save
member['full_name'] = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()

# Save to database
print(f"\nSaving to database...")
db = DatabaseManager()
success = db.save_members_to_db([member])

if not success:
    print("ERROR: Failed to save to database")
    sys.exit(1)

print("OK - Saved to database")

# Read back from database
print(f"\nReading back from database...")
member_id = member.get('id') or member.get('prospectId')
result = db.execute_query("""
    SELECT full_name, address, city, state, zip_code
    FROM members
    WHERE prospect_id = ?
""", (member_id,), fetch_one=True)

if result:
    result_dict = dict(result)
    print(f"\nMember in database:")
    print(f"  Name: {result_dict.get('full_name')}")
    print(f"  Address: {result_dict.get('address')}")
    print(f"  City: {result_dict.get('city')}")
    print(f"  State: {result_dict.get('state')}")
    print(f"  Zip: {result_dict.get('zip_code')}")

    # Verify address is not NULL
    if result_dict.get('address'):
        print(f"\n*** SUCCESS! Address was saved correctly! ***")
    else:
        print(f"\n*** FAILED! Address is still NULL ***")
else:
    print("ERROR: Member not found in database")
