#!/usr/bin/env python3
"""
Find Jeremy Mayo in ClubHub members and prospects at different gym locations
"""

from services.api.clubhub_api_client import ClubHubAPIClient
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

def find_jeremy_mayo():
    """Search for Jeremy Mayo in ClubHub data at different gym locations"""
    
    print("🔍 Searching for Jeremy Mayo in ClubHub at different gym locations...")
    print("=" * 70)
    
    # Create API client and authenticate
    client = ClubHubAPIClient()
    success = client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD)
    
    if not success:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Try different club IDs for different gym locations
    # Club 1156 is Seymour - let's try other common club IDs
    club_ids_to_try = [
        1156,  # Seymour (current)
        1157,  # Fond du Lac (common nearby location)
        1158,  # Appleton
        1159,  # Oshkosh
        1160,  # Green Bay
        1161,  # Milwaukee
        1162,  # Madison
        1163,  # Waukesha
        1164,  # Racine
        1165,  # Kenosha
        1001,  # Common test club ID
        1002,  # Another common test club ID
    ]
    
    jeremy_found = False
    
    for club_id in club_ids_to_try:
        print(f"\n🏢 Searching Club ID {club_id}...")
        
        # Update the API URLs for this club
        members_url = f"https://clubhub-ios-api.anytimefitness.com/api/v1.0/clubs/{club_id}/members"
        prospects_url = f"https://clubhub-ios-api.anytimefitness.com/api/v1.0/clubs/{club_id}/prospects"
        
        # Search in members
        print(f"   📋 Searching members...")
        jeremy_member = None
        page = 1
        
        while True:
            try:
                members = client.get_all_members(page=page, page_size=50, club_id=club_id)
                if not members:
                    break
                    
                print(f"      Checking page {page} ({len(members)} members)...")
                
                for member in members:
                    first_name = member.get('firstName', '').lower()
                    last_name = member.get('lastName', '').lower()
                    
                    if 'jeremy' in first_name and 'mayo' in last_name:
                        jeremy_member = member
                        print(f"      ✅ Found Jeremy Mayo in members at Club {club_id}!")
                        print(f"         Name: {member.get('firstName')} {member.get('lastName')}")
                        print(f"         ID: {member.get('id')}")
                        print(f"         ProspectID: {member.get('prospectId', 'N/A')}")
                        print(f"         Email: {member.get('email', 'N/A')}")
                        print(f"         Phone: {member.get('phone', 'N/A')}")
                        jeremy_found = True
                        break
                
                if jeremy_member:
                    break
                    
                page += 1
                if page > 5:  # Limit search to 5 pages per club
                    break
                    
            except Exception as e:
                print(f"      ⚠️ Error searching members at Club {club_id}: {e}")
                break
        
        if jeremy_member:
            break
        
        # Search in prospects
        print(f"   👥 Searching prospects...")
        jeremy_prospect = None
        page = 1
        
        while True:
            try:
                prospects = client.get_all_prospects(page=page, page_size=50, club_id=club_id)
                if not prospects:
                    break
                    
                print(f"      Checking page {page} ({len(prospects)} prospects)...")
                
                for prospect in prospects:
                    first_name = prospect.get('firstName', '').lower()
                    last_name = prospect.get('lastName', '').lower()
                    
                    if 'jeremy' in first_name and 'mayo' in last_name:
                        jeremy_prospect = prospect
                        print(f"      ✅ Found Jeremy Mayo in prospects at Club {club_id}!")
                        print(f"         Name: {prospect.get('firstName')} {prospect.get('lastName')}")
                        print(f"         ID: {prospect.get('id')}")
                        print(f"         ProspectID: {prospect.get('prospectId', 'N/A')}")
                        print(f"         Email: {prospect.get('email', 'N/A')}")
                        print(f"         Phone: {prospect.get('phone', 'N/A')}")
                        jeremy_found = True
                        break
                
                if jeremy_prospect:
                    break
                    
                page += 1
                if page > 5:  # Limit search to 5 pages per club
                    break
                    
            except Exception as e:
                print(f"      ⚠️ Error searching prospects at Club {club_id}: {e}")
                break
        
        if jeremy_prospect:
            break
    
    if not jeremy_found:
        print("\n❌ Jeremy Mayo not found in any of the searched gym locations")
        print("   This could mean:")
        print("   - You're at a different gym location")
        print("   - Your profile uses a different name format")
        print("   - You're not in the ClubHub system")
    
    return jeremy_found

if __name__ == "__main__":
    find_jeremy_mayo() 