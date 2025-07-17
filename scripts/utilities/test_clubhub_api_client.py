#!/usr/bin/env python3
"""
Test ClubHub API Client with updated headers and authentication
"""

from services.api.clubhub_api_client import ClubHubAPIClient
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

def test_clubhub_authentication():
    """Test ClubHub authentication with updated client"""
    
    print("🚀 Testing ClubHub API Client with HAR-based authentication...")
    print("=" * 60)
    
    # Create API client
    client = ClubHubAPIClient()
    
    # Test authentication
    print("1. Testing authentication...")
    success = client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD)
    
    if not success:
        print("❌ Authentication failed. Cannot proceed with API tests.")
        return False
    
    print("\n2. Testing API endpoints...")
    
    # Test club features
    print("   Testing club features...")
    features = client.get_club_features()
    if features:
        print("   ✅ Club features endpoint works")
    else:
        print("   ❌ Club features endpoint failed")
    
    # Test members endpoint
    print("   Testing members endpoint...")
    members = client.get_all_members(page=1, page_size=10)
    if members:
        print(f"   ✅ Members endpoint works - found {len(members)} members")
        if members:
            first_member = members[0]
            print(f"   📋 First member: {first_member.get('firstName', 'N/A')} {first_member.get('lastName', 'N/A')}")
    else:
        print("   ❌ Members endpoint failed")
    
    # Test prospects endpoint
    print("   Testing prospects endpoint...")
    prospects = client.get_all_prospects(page=1, page_size=10)
    if prospects:
        print(f"   ✅ Prospects endpoint works - found {len(prospects)} prospects")
        if prospects:
            first_prospect = prospects[0]
            print(f"   📋 First prospect: {first_prospect.get('firstName', 'N/A')} {first_prospect.get('lastName', 'N/A')}")
    else:
        print("   ❌ Prospects endpoint failed")
    
    # Search for Jeremy Mayo specifically
    print("\n3. Searching for Jeremy Mayo...")
    if members:
        jeremy_found = False
        for member in members:
            if 'jeremy' in member.get('firstName', '').lower() or 'mayo' in member.get('lastName', '').lower():
                print(f"   ✅ Found Jeremy Mayo: {member.get('firstName')} {member.get('lastName')} (ID: {member.get('id')})")
                jeremy_found = True
                break
        
        if not jeremy_found:
            print("   ❌ Jeremy Mayo not found in members")
    
    if prospects:
        jeremy_found = False
        for prospect in prospects:
            if 'jeremy' in prospect.get('firstName', '').lower() or 'mayo' in prospect.get('lastName', '').lower():
                print(f"   ✅ Found Jeremy Mayo in prospects: {prospect.get('firstName')} {prospect.get('lastName')} (ID: {prospect.get('id')})")
                jeremy_found = True
                break
        
        if not jeremy_found:
            print("   ❌ Jeremy Mayo not found in prospects")
    
    print("\n✅ ClubHub API Client test completed!")
    return True

if __name__ == "__main__":
    test_clubhub_authentication() 