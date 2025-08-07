#!/usr/bin/env python3
"""
Debug and fix the 404 endpoints for training package discovery
"""

import sys
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
import json
import time

def debug_training_endpoints():
    """Debug why training endpoints return 404 and try to fix them"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print("🔍 Debugging training package endpoints...")
    print("=" * 70)
    
    # First, let's see what cookies and session state we have
    print("🍪 Current session cookies:")
    for cookie in api.session.cookies:
        print(f"   {cookie.name}: {cookie.value[:50]}...")
    
    print(f"\n🔗 Current session headers:")
    for header, value in api.session.headers.items():
        print(f"   {header}: {value}")
    
    # Test various training-related endpoints with different approaches
    training_endpoints = [
        # Basic training endpoints
        "/api/training/packages",
        "/api/training/clients", 
        "/api/training/agreements",
        "/api/packages",
        "/api/agreements",
        
        # Member-specific training endpoints  
        "/api/members/training",
        "/api/members/packages",
        "/api/members/agreements",
        
        # Agreement-specific endpoints
        "/api/agreements/packages",
        "/api/agreements/training",
        "/api/agreements/list",
        
        # Package-specific endpoints
        "/api/packages/agreements", 
        "/api/packages/training",
        "/api/packages/list",
        
        # Action endpoints (like the working delegation)
        "/action/Training",
        "/action/Packages", 
        "/action/Agreements",
        "/action/Training/packages",
        "/action/Training/clients",
        
        # ClubServices related
        "/action/ClubServices",
        "/action/ClubServices/training",
        "/action/ClubServices/packages",
    ]
    
    print(f"\n🧪 Testing training endpoints...")
    
    for endpoint in training_endpoints:
        print(f"\n📍 Testing: {endpoint}")
        
        # Try GET request
        try:
            response = api.session.get(f"{api.base_url}{endpoint}")
            print(f"   GET status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ SUCCESS! JSON response: {json.dumps(data, indent=2)[:300]}...")
                except:
                    print(f"   ✅ SUCCESS! HTML response length: {len(response.text)}")
                    if "training" in response.text.lower() or "package" in response.text.lower():
                        print(f"   🎯 Contains training/package content!")
            elif response.status_code == 404:
                print(f"   ❌ 404 Not Found")
            else:
                print(f"   ⚠️  Status {response.status_code}: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ GET Error: {e}")
        
        # Try POST request with empty data
        try:
            response = api.session.post(f"{api.base_url}{endpoint}", json={})
            print(f"   POST status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ POST SUCCESS! JSON: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   ✅ POST SUCCESS! HTML length: {len(response.text)}")
        except Exception as e:
            print(f"   ❌ POST Error: {e}")

def test_working_endpoints_with_params():
    """Test the working delegation endpoint with different parameters"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print(f"\n🎯 Testing working delegation endpoint with variations...")
    print("=" * 70)
    
    # Test the working delegation URL with different IDs
    test_ids = [
        "189425730",  # Dennis's working delegate ID
        "65828815",   # Dennis's CSV member ID
        "1",          # Simple test
        "100",        # Another test
    ]
    
    for test_id in test_ids:
        print(f"\n🔬 Testing delegation with ID: {test_id}")
        
        # Test different URL variations
        delegation_urls = [
            f"/action/Delegate/{test_id}/url=false",  # Original working format
            f"/action/Delegate/{test_id}",            # Without url parameter
            f"/action/Delegate/{test_id}/url=true",   # With url=true
            f"/action/Delegate?id={test_id}",         # Query parameter format
            f"/action/Delegate?memberId={test_id}",   # Different parameter name
        ]
        
        for url in delegation_urls:
            try:
                response = api.session.get(f"{api.base_url}{url}")
                print(f"   {url}: {response.status_code}")
                
                if response.status_code == 200:
                    # After successful delegation, try the package agreements
                    agreements_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
                    print(f"     → Agreements: {agreements_response.status_code}")
                    
                    if agreements_response.status_code == 200:
                        agreements = agreements_response.json()
                        print(f"     → Found {len(agreements)} agreements!")
                        
                        if agreements:
                            for i, agreement in enumerate(agreements[:2]):  # Show first 2
                                package_info = agreement.get('packageAgreement', {})
                                name = package_info.get('name', 'No name')
                                member_id = package_info.get('memberId', 'No member ID')
                                print(f"       Agreement {i+1}: {name} (Member: {member_id})")
            except Exception as e:
                print(f"   {url}: Error - {e}")

def explore_api_discovery():
    """Try to discover available API endpoints"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print(f"\n🗺️  Exploring API discovery...")
    print("=" * 70)
    
    # Try common API discovery endpoints
    discovery_endpoints = [
        "/api",
        "/api/",
        "/api/help",
        "/api/docs",
        "/api/swagger",
        "/api/openapi",
        "/api/v1",
        "/api/v2",
        "/help",
        "/docs",
        "/.well-known/api",
    ]
    
    for endpoint in discovery_endpoints:
        try:
            response = api.session.get(f"{api.base_url}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"     ✅ SUCCESS! Response length: {len(response.text)}")
                if response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        data = response.json()
                        print(f"     JSON keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    except:
                        pass
        except Exception as e:
            print(f"   {endpoint}: Error - {e}")

def test_different_authentication_states():
    """Test endpoints in different authentication states"""
    
    print(f"\n🔐 Testing different authentication states...")
    print("=" * 70)
    
    api = ClubOSTrainingPackageAPI()
    
    # Test without authentication
    print("📝 Testing WITHOUT authentication...")
    test_url = f"{api.base_url}/api/agreements/package_agreements/list"
    
    try:
        response = api.session.get(test_url)
        print(f"   Without auth: {response.status_code}")
    except Exception as e:
        print(f"   Without auth: Error - {e}")
    
    # Test with authentication
    print("📝 Testing WITH authentication...")
    if api.authenticate():
        try:
            response = api.session.get(test_url)
            print(f"   With auth: {response.status_code}")
        except Exception as e:
            print(f"   With auth: Error - {e}")
    
    # Test with delegation set
    print("📝 Testing WITH authentication AND delegation...")
    if api.authenticate():
        # Set delegation to Dennis's working ID
        delegation_response = api.session.get(f"{api.base_url}/action/Delegate/189425730/url=false")
        print(f"   Delegation setup: {delegation_response.status_code}")
        
        if delegation_response.status_code == 200:
            try:
                response = api.session.get(test_url)
                print(f"   With auth + delegation: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   🎯 SUCCESS! Found {len(data)} agreements")
            except Exception as e:
                print(f"   With auth + delegation: Error - {e}")

if __name__ == "__main__":
    debug_training_endpoints()
    test_working_endpoints_with_params()
    explore_api_discovery()
    test_different_authentication_states()
    
    print("\n" + "=" * 70)
    print("🏁 Debug complete!")
