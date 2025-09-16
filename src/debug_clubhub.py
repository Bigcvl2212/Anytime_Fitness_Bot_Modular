#!/usr/bin/env python3
"""
Debug ClubHub API to see what data is actually being returned
"""

from main_app import create_app
from src.services.api.clubhub_api_client import ClubHubAPIClient
from src.services.authentication.secure_secrets_manager import SecureSecretsManager
import json

app = create_app()
with app.app_context():
    print('🔍 DEBUGGING ClubHub API directly...')
    print('=' * 60)
    
    # Test ClubHub API directly
    secrets_manager = SecureSecretsManager()
    CLUBHUB_EMAIL = secrets_manager.get_secret('clubhub-email')
    CLUBHUB_PASSWORD = secrets_manager.get_secret('clubhub-password')
    
    print(f'ClubHub Email: {CLUBHUB_EMAIL}')
    print(f'ClubHub Password: {"*" * len(CLUBHUB_PASSWORD) if CLUBHUB_PASSWORD else "None"}')
    
    if CLUBHUB_EMAIL and CLUBHUB_PASSWORD:
        clubhub_client = ClubHubAPIClient()
        
        if clubhub_client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
            print('✅ Authentication successful!')
            
            # Test members endpoint
            print('\n📊 Testing members endpoint...')
            members_response = clubhub_client.get_all_members(page=1, page_size=10)
            print(f'Members response type: {type(members_response)}')
            
            if members_response:
                if isinstance(members_response, dict):
                    print(f'Members response keys: {list(members_response.keys())}')
                    print(f'Full members response:')
                    print(json.dumps(members_response, indent=2)[:1000] + '...' if len(str(members_response)) > 1000 else json.dumps(members_response, indent=2))
                else:
                    print(f'Members response (not dict): {members_response}')
            else:
                print('❌ No members response')
            
            # Test prospects endpoint  
            print('\n📈 Testing prospects endpoint...')
            prospects_response = clubhub_client.get_all_prospects(page=1, page_size=10)
            print(f'Prospects response type: {type(prospects_response)}')
            
            if prospects_response:
                if isinstance(prospects_response, dict):
                    print(f'Prospects response keys: {list(prospects_response.keys())}')
                    print(f'Full prospects response:')
                    print(json.dumps(prospects_response, indent=2)[:1000] + '...' if len(str(prospects_response)) > 1000 else json.dumps(prospects_response, indent=2))
                else:
                    print(f'Prospects response (not dict): {prospects_response}')
            else:
                print('❌ No prospects response')
                
            # Try different club ID or parameters
            print('\n🔄 Trying different parameters...')
            alt_members = clubhub_client.get_all_members(
                page=1, 
                page_size=50,
                extra_params={
                    "status": "active",
                    "days": "30"
                }
            )
            print(f'Alternative members call: {type(alt_members)} - {bool(alt_members)}')
            if alt_members and isinstance(alt_members, dict):
                print(f'Alt members keys: {list(alt_members.keys())}')
                
        else:
            print('❌ Authentication failed')
    else:
        print('❌ Missing credentials')