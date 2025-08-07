#!/usr/bin/env python3
"""
Find Dennis's actual ClubOS delegate user ID by searching through various ClubOS APIs
"""

import sys
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
import re
import json
import time
from datetime import datetime

def decode_jwt_payload(token):
    """Decode JWT payload without verification"""
    try:
        import base64
        parts = token.split('.')
        if len(parts) >= 2:
            payload = parts[1]
            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.b64decode(payload)
            return json.loads(decoded)
    except:
        return None

def search_for_dennis_in_various_apis():
    """Search for Dennis using different ClubOS API endpoints"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print("🔍 Searching for Dennis Rost in various ClubOS endpoints...")
    
    # Try to find Dennis in member search/list endpoints
    search_terms = [
        "Dennis Rost",
        "Dennis",
        "Rost", 
        "dennis.rost",
        "dennis"
    ]
    
    # Test different API endpoints that might list members
    endpoints_to_test = [
        "/api/agreements/package_agreements/search",
        "/api/members/search",
        "/api/members/list", 
        "/api/delegation/members",
        "/api/billing/members",
        "/api/training/clients",
        "/api/clubservices/members"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n📡 Testing {endpoint}")
        
        # Try GET request
        try:
            response = api.session.get(f"{api.base_url}{endpoint}")
            print(f"   GET {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response type: {type(data)}, length: {len(data) if isinstance(data, (list, dict)) else 'N/A'}")
                
                # Search for Dennis in the response
                response_text = str(data).lower()
                if 'dennis' in response_text or 'rost' in response_text:
                    print(f"   🎯 FOUND DENNIS REFERENCE in {endpoint}!")
                    print(f"   Data: {json.dumps(data, indent=2)[:500]}...")
                    
        except Exception as e:
            print(f"   Error with GET {endpoint}: {e}")
            
        # Try POST with search terms
        for term in search_terms[:2]:  # Just try first couple terms
            try:
                response = api.session.post(f"{api.base_url}{endpoint}", json={"search": term})
                if response.status_code == 200:
                    data = response.json()
                    response_text = str(data).lower()
                    if 'dennis' in response_text or 'rost' in response_text:
                        print(f"   🎯 FOUND DENNIS in POST {endpoint} with search '{term}'!")
                        print(f"   Data: {json.dumps(data, indent=2)[:500]}...")
            except:
                pass
                
        time.sleep(0.5)  # Rate limit
    
    # Let's also try to get the current Bearer token and decode it
    print(f"\n🔐 Current session info:")
    print(f"   Session cookies: {list(api.session.cookies.keys())}")
    
    # Try to extract access token from a page that might have it
    try:
        print(f"\n📄 Checking PackageAgreementUpdated page for current token...")
        response = api.session.get(f"{api.base_url}/action/PackageAgreementUpdated")
        if response.status_code == 200:
            # Look for ACCESS_TOKEN pattern
            token_match = re.search(r'var ACCESS_TOKEN = ["\']([^"\']+)["\']', response.text)
            if token_match:
                current_token = token_match.group(1)
                print(f"   Found current Bearer token")
                
                # Decode the token
                payload = decode_jwt_payload(current_token)
                if payload:
                    print(f"   Token payload: {json.dumps(payload, indent=2)}")
                    logged_in_user_id = payload.get('loggedInUserId')
                    print(f"   Your logged-in user ID: {logged_in_user_id}")
                    
                    # Try to find members you can delegate to
                    print(f"\n🔄 Testing delegation with your user ID...")
                    delegate_url = f"{api.base_url}/api/delegation/users/{logged_in_user_id}/delegate"
                    delegate_response = api.session.post(delegate_url)
                    print(f"   Delegation response: {delegate_response.status_code}")
                    
                    if delegate_response.status_code == 200:
                        # Now try to list all members you can see
                        list_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
                        print(f"   Package agreements list: {list_response.status_code}")
                        if list_response.status_code == 200:
                            agreements = list_response.json()
                            print(f"   Found {len(agreements)} agreements total")
                            
                            # Look for Dennis in the agreements
                            for agreement in agreements:
                                member_name = str(agreement.get('member', {})).lower()
                                if 'dennis' in member_name or 'rost' in member_name:
                                    print(f"   🎯 FOUND DENNIS in agreements: {agreement}")
    except Exception as e:
        print(f"   Error extracting token: {e}")

def test_known_member_ids():
    """Test the IDs we already know for Dennis"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        return
        
    known_dennis_ids = [
        65828815,    # ClubHub ID
        96530079,    # CSV agreement_agreementID  
        31489560,    # CSV userId
        "65828815",  # String versions
        "96530079",
        "31489560"
    ]
    
    print(f"\n🧪 Testing known Dennis IDs for delegation...")
    
    for member_id in known_dennis_ids:
        print(f"\n   Testing delegation to ID: {member_id}")
        try:
            delegate_url = f"{api.base_url}/api/delegation/users/{member_id}/delegate"
            response = api.session.post(delegate_url)
            print(f"   Delegation status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Delegation successful for ID {member_id}")
                
                # Try to get agreements for this ID
                agreements_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
                print(f"   Agreements status: {agreements_response.status_code}")
                
                if agreements_response.status_code == 200:
                    agreements = agreements_response.json()
                    print(f"   Found {len(agreements)} agreements for ID {member_id}")
                    
                    if agreements:
                        print(f"   Sample agreement: {json.dumps(agreements[0], indent=2)}")
                        
                        # Check if any mention Dennis
                        for agreement in agreements:
                            agreement_text = str(agreement).lower()
                            if 'dennis' in agreement_text or 'rost' in agreement_text:
                                print(f"   🎯 FOUND DENNIS DATA: {agreement}")
                        
            else:
                print(f"   ❌ Delegation failed: {response.text[:200]}")
                
        except Exception as e:
            print(f"   Error testing ID {member_id}: {e}")
            
        time.sleep(0.5)

if __name__ == "__main__":
    print("🔍 Finding Dennis's ClubOS delegate user ID...")
    print("=" * 60)
    
    # First try the general search
    search_for_dennis_in_various_apis()
    
    # Then test our known IDs
    test_known_member_ids()
    
    print("\n" + "=" * 60)
    print("🏁 Search complete!")
