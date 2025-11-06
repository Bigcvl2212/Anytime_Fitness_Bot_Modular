#!/usr/bin/env python3
"""
Test what ClubHub API actually returns for member data
"""
import sys
sys.path.insert(0, '.')

from src.services.api.clubhub_api_client import ClubHubAPIClient
from src.services.authentication.secure_secrets_manager import SecureSecretsManager
import json

# Get credentials
import os
os.environ['FLASK_SECRET_KEY'] = '8CjA9r9dxVjMkhONTOQuSWoPRJPquoatLY9Hz5wVm_M'

secrets_manager = SecureSecretsManager()
creds = secrets_manager.get_credentials('ef8de92f-f6b5-43')

clubhub_email = creds.get('clubhub_email') if creds else None
clubhub_password = creds.get('clubhub_password') if creds else None

# Authenticate
client = ClubHubAPIClient()
client.club_id = '1156'  # Fond du Lac

if clubhub_email and clubhub_password:
    if client.authenticate(clubhub_email, clubhub_password):
        print("Authenticated with ClubHub")

        # Get a specific member we know exists
        print("\nTesting members API...")
        members_response = client.get_all_members(page=1, page_size=1, club_id='1156')

        if members_response and len(members_response) > 0:
            member = members_response[0]
            print(f"\nSample member - ALL fields:")
            print(json.dumps(member, indent=2, default=str))

            print(f"\nAddress-related fields found:")
            for key, value in member.items():
                if any(addr_word in key.lower() for addr_word in ['address', 'street', 'city', 'state', 'zip', 'postal', 'mail']):
                    print(f"  {key}: {value}")

        print("\nTesting prospects API...")
        prospects_response = client.get_all_prospects(page=1, page_size=1, club_id='1156')

        if prospects_response and len(prospects_response) > 0:
            prospect = prospects_response[0]
            print(f"\nSample prospect - ALL fields:")
            print(json.dumps(prospect, indent=2, default=str))

            print(f"\nAddress-related fields found:")
            for key, value in prospect.items():
                if any(addr_word in key.lower() for addr_word in ['address', 'street', 'city', 'state', 'zip', 'postal', 'mail']):
                    print(f"  {key}: {value}")
    else:
        print("Auth failed")
else:
    print("No credentials")
