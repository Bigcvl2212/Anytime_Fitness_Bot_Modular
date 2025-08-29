#!/usr/bin/env python3
"""
Test multiple club IDs to find all prospects across clubs
"""

import sys
import os
sys.path.append('src/services')
from api.clubhub_api_client import ClubHubAPIClient
sys.path.append('src/config')
from clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

def test_multi_club_prospects():
    print('🌐 Testing multiple club IDs to find all prospects...')
    client = ClubHubAPIClient()
    
    if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
        print('❌ ClubHub authentication failed')
        return
    
    # Check what clubs you have access to first
    print('\n🏢 Checking user clubs...')
    try:
        # Get user details to find all clubs
        auth_data = client._make_request("GET", f"{client.base_url}/api/user")
        if auth_data:
            print(f'👤 User data: {auth_data}')
            
        # Try to get user clubs
        user_clubs = client._make_request("GET", f"{client.base_url}/api/user/clubs")
        if user_clubs:
            print(f'🏢 User clubs: {user_clubs}')
    except Exception as e:
        print(f'⚠️ Could not get user clubs: {e}')
    
    # Test known club IDs
    club_ids_to_test = [
        "1156",  # Current default
        "1657",  # From working script token (club_ids: ["1156", "1657"])
        "2377",  # From HAR file
        "1643",  # From HAR file notify call
    ]
    
    total_prospects = 0
    all_prospects = []
    
    for club_id in club_ids_to_test:
        print(f'\n🏢 Testing club ID: {club_id}...')
        
        try:
            # Test a single page first
            response = client.get_all_prospects(page=1, page_size=10, club_id=club_id)
            if response:
                prospects = response if isinstance(response, list) else response.get('prospects', [])
                if prospects:
                    print(f'✅ Club {club_id}: Found {len(prospects)} prospects on page 1')
                    
                    # Get all prospects for this club
                    print(f'🔍 Getting ALL prospects for club {club_id}...')
                    club_prospects = []
                    page = 1
                    
                    while True:
                        response = client.get_all_prospects(page=page, page_size=100, club_id=club_id)
                        if not response:
                            break
                            
                        page_prospects = response if isinstance(response, list) else response.get('prospects', [])
                        if not page_prospects:
                            break
                            
                        club_prospects.extend(page_prospects)
                        print(f'  📄 Page {page}: {len(page_prospects)} prospects (Total for club {club_id}: {len(club_prospects)})')
                        
                        if len(page_prospects) < 100:
                            break
                        page += 1
                    
                    print(f'🎯 Club {club_id} TOTAL: {len(club_prospects)} prospects')
                    total_prospects += len(club_prospects)
                    all_prospects.extend(club_prospects)
                    
                    # Show sample from this club
                    if club_prospects:
                        sample = club_prospects[0]
                        name = f"{sample.get('firstName', '')} {sample.get('lastName', '')}".strip()
                        print(f'  📋 Sample: {name} - {sample.get("email", "")}')
                        
                else:
                    print(f'📭 Club {club_id}: No prospects found')
            else:
                print(f'❌ Club {club_id}: API call failed')
                
        except Exception as e:
            print(f'❌ Club {club_id}: Error - {e}')
    
    print(f'\n🎉 FINAL MULTI-CLUB RESULT: {total_prospects} prospects across {len(club_ids_to_test)} clubs')
    
    if all_prospects:
        print(f'📊 Total unique prospects collected: {len(all_prospects)}')
        
        # Save combined results
        import json
        with open("multi_club_prospects.json", "w") as f:
            json.dump(all_prospects, f)
        print('💾 Saved all prospects to multi_club_prospects.json')

if __name__ == "__main__":
    test_multi_club_prospects()
