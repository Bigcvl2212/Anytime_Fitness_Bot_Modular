#!/usr/bin/env python3

import sys
import os
sys.path.append('src/services')
from api.clubhub_api_client import ClubHubAPIClient
sys.path.append('src/config')
from clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

def main():
    print('🔍 Testing ClubHub prospects API with fresh authentication...')
    client = ClubHubAPIClient()
    
    if client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
        print('✅ ClubHub authenticated')
        
        # Test the exact same prospects endpoint as the working script
        prospects_response = client.get_all_prospects(page=1, page_size=100)
        print(f'Prospects API response type: {type(prospects_response)}')
        
        if prospects_response:
            if isinstance(prospects_response, dict):
                prospects = prospects_response.get('prospects', [])
                print(f'Found {len(prospects)} prospects on first page')
                if prospects:
                    print('First prospect example:')
                    prospect = prospects[0]
                    print(f'  Name: {prospect.get("firstName", "")} {prospect.get("lastName", "")}')
                    print(f'  Email: {prospect.get("email", "No email")}')
                    print(f'  Keys in prospect: {list(prospect.keys())}')
                else:
                    print('No prospects in response')
                    print(f'Response keys: {list(prospects_response.keys())}')
            else:
                print(f'Unexpected response type: {type(prospects_response)}')
                print(f'Response content: {prospects_response}')
        else:
            print('❌ No response from prospects API')
    else:
        print('❌ ClubHub authentication failed')

if __name__ == "__main__":
    main()
