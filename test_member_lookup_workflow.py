#!/usr/bin/env python3
"""
Test the member lookup workflow to set delegate context
This mimics the manual process: search member -> account page -> clubservices page
"""

import sys
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
import json
import time
from urllib.parse import quote

def test_member_lookup_workflow():
    """Test the full member lookup workflow that sets delegate context"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print("🔍 Testing member lookup workflow for Dennis Rost...")
    
    # Step 1: Search for Dennis by name (like the manual process)
    search_term = "Dennis Rost"
    print(f"\n📝 Step 1: Searching for member '{search_term}'...")
    
    # Try the member search endpoint
    search_url = f"{api.base_url}/api/members/search"
    search_params = {
        'q': search_term,
        'limit': 10
    }
    
    search_response = api.session.get(search_url, params=search_params)
    print(f"   Search status: {search_response.status_code}")
    
    if search_response.status_code == 200:
        search_results = search_response.json()
        print(f"   Found {len(search_results)} search results")
        
        # Look for Dennis in results
        dennis_result = None
        for result in search_results:
            name = result.get('name', '').lower()
            if 'dennis' in name and 'rost' in name:
                dennis_result = result
                break
        
        if dennis_result:
            member_id = dennis_result.get('id')
            print(f"   ✅ Found Dennis in search results with ID: {member_id}")
            print(f"   Dennis data: {json.dumps(dennis_result, indent=2)}")
            
            # Step 2: Navigate to Dennis's account page
            print(f"\n👤 Step 2: Navigating to Dennis's account page...")
            account_url = f"{api.base_url}/action/Member/{member_id}/view"
            account_response = api.session.get(account_url)
            print(f"   Account page status: {account_response.status_code}")
            
            if account_response.status_code == 200:
                # Step 3: Navigate to ClubServices page (this should set delegate context)
                print(f"\n🏋️ Step 3: Navigating to ClubServices page...")
                clubservices_url = f"{api.base_url}/action/Member/{member_id}/clubservices"
                clubservices_response = api.session.get(clubservices_url)
                print(f"   ClubServices page status: {clubservices_response.status_code}")
                
                if clubservices_response.status_code == 200:
                    # Step 4: Now try to get package agreements (should work with delegate context set)
                    print(f"\n📦 Step 4: Getting package agreements with delegate context set...")
                    
                    # Wait a moment for any session state to settle
                    time.sleep(1)
                    
                    agreements_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
                    print(f"   Agreements status: {agreements_response.status_code}")
                    
                    if agreements_response.status_code == 200:
                        agreements = agreements_response.json()
                        print(f"   ✅ Found {len(agreements)} agreements after workflow!")
                        
                        if agreements:
                            for i, agreement in enumerate(agreements):
                                package_info = agreement.get('packageAgreement', {})
                                package_name = package_info.get('name', 'No name')
                                package_member_id = package_info.get('memberId', 'No member ID')
                                print(f"      Agreement {i+1}: {package_name} (Member ID: {package_member_id})")
                                
                            # This should be Dennis's training package!
                            return member_id, agreements
                        else:
                            print("   ❌ No agreements found even after workflow")
                    else:
                        print(f"   ❌ Failed to get agreements: {agreements_response.status_code}")
                else:
                    print(f"   ❌ Failed to load ClubServices page: {clubservices_response.status_code}")
            else:
                print(f"   ❌ Failed to load account page: {account_response.status_code}")
        else:
            print("   ❌ Dennis not found in search results")
            print(f"   All results: {json.dumps(search_results, indent=2)}")
    else:
        print(f"   ❌ Search failed: {search_response.status_code}")
        print(f"   Response: {search_response.text[:500]}...")

def test_alternative_search_endpoints():
    """Try alternative search endpoints"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print("\n🔍 Testing alternative search endpoints...")
    
    search_endpoints = [
        "/api/members/find",
        "/api/members/lookup", 
        "/api/search/members",
        "/action/Member/search",
        "/action/Members/search"
    ]
    
    search_term = "Dennis Rost"
    
    for endpoint in search_endpoints:
        print(f"\n📍 Testing endpoint: {endpoint}")
        
        # Try GET request
        url = f"{api.base_url}{endpoint}"
        try:
            response = api.session.get(url, params={'q': search_term, 'name': search_term, 'search': search_term})
            print(f"   GET status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   GET response: {json.dumps(data, indent=2)[:500]}...")
                except:
                    print(f"   GET response (text): {response.text[:200]}...")
            
            # Try POST request
            response = api.session.post(url, json={'q': search_term, 'name': search_term, 'search': search_term})
            print(f"   POST status: {response.status_code}")
            
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    print("🔍 Testing member lookup workflow to set delegate context...")
    print("=" * 70)
    
    test_member_lookup_workflow()
    
    print("\n" + "=" * 70)
    print("🔍 Testing alternative search methods...")
    
    test_alternative_search_endpoints()
    
    print("\n" + "=" * 70)
    print("🏁 Test complete!")
