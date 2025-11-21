#!/usr/bin/env python3
"""
Square Application Type Detection
"""
import requests
import json
import sys
import os
sys.path.append('src')

from config.secrets_local import get_secret

def test_different_square_endpoints():
    """Test various Square API endpoints to identify the token type"""
    print("🔍 SQUARE APPLICATION TYPE DETECTION")
    print("=" * 50)
    
    prod_token = get_secret("square-production-access-token")
    sandbox_token = get_secret("square-sandbox-access-token")
    
    # Different base URLs and endpoints to try
    endpoints_to_test = [
        # Standard Connect API
        ("Connect API v2 (Production)", "https://connect.squareup.com/v2/locations", prod_token),
        ("Connect API v2 (Sandbox)", "https://connect.squareupsandbox.com/v2/locations", sandbox_token),
        
        # Older API versions
        ("Connect API v1 (Production)", "https://connect.squareup.com/v1/me/locations", prod_token),
        ("Connect API v1 (Sandbox)", "https://connect.squareupsandbox.com/v1/me/locations", sandbox_token),
        
        # Try without Square-Version header
        ("Connect API v2 No Version (Production)", "https://connect.squareup.com/v2/locations", prod_token),
    ]
    
    for name, url, token in endpoints_to_test:
        print(f"\n🎯 Testing: {name}")
        print(f"   URL: {url}")
        
        # Base headers
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Add Square-Version for v2 endpoints (except the test without it)
        if 'v2' in url and 'No Version' not in name:
            headers['Square-Version'] = '2024-07-17'
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS!")
                try:
                    data = response.json()
                    if 'locations' in data:
                        locations = data['locations']
                        print(f"   Found {len(locations)} locations")
                        for loc in locations[:2]:
                            name_key = 'name' if 'name' in loc else 'business_name'
                            id_key = 'id' if 'id' in loc else 'location_id'
                            print(f"     - {loc.get(name_key, 'Unknown')} ({loc.get(id_key, 'No ID')})")
                    else:
                        print(f"   Response: {json.dumps(data, indent=2)[:300]}...")
                except json.JSONDecodeError:
                    print(f"   Non-JSON response: {response.text[:200]}...")
                    
            elif response.status_code == 401:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('errors', [{}])[0].get('detail', 'No detail')
                    print(f"   ❌ 401: {error_detail}")
                except:
                    print(f"   ❌ 401: {response.text[:100]}...")
                    
            elif response.status_code == 404:
                print(f"   ❌ 404: Endpoint not found")
                
            else:
                try:
                    error_data = response.json()
                    print(f"   ❌ {response.status_code}: {error_data}")
                except:
                    print(f"   ❌ {response.status_code}: {response.text[:100]}...")
                    
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")

def check_token_permissions():
    """Try to determine what permissions these tokens might have"""
    print(f"\n🔐 TOKEN PERMISSIONS TEST")
    print("=" * 40)
    
    prod_token = get_secret("square-production-access-token")
    
    # Test endpoints that require different permissions
    permission_tests = [
        ("Basic Info", "https://connect.squareup.com/v2/merchants"),
        ("Locations", "https://connect.squareup.com/v2/locations"), 
        ("Catalog", "https://connect.squareup.com/v2/catalog/list"),
        ("Customers", "https://connect.squareup.com/v2/customers"),
        ("Orders", "https://connect.squareup.com/v2/orders/search"),
        ("Payments", "https://connect.squareup.com/v2/payments"),
        ("Invoices", "https://connect.squareup.com/v2/invoices")
    ]
    
    headers = {
        'Authorization': f'Bearer {prod_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Square-Version': '2024-07-17'
    }
    
    for name, endpoint in permission_tests:
        try:
            if 'search' in endpoint:
                # POST request for search endpoints
                response = requests.post(endpoint, headers=headers, json={}, timeout=10)
            else:
                # GET request for list endpoints
                response = requests.get(endpoint, headers=headers, timeout=10)
                
            print(f"{name:12} - Status: {response.status_code}", end="")
            
            if response.status_code == 200:
                print(" ✅ AUTHORIZED")
            elif response.status_code == 401:
                print(" ❌ UNAUTHORIZED")
            elif response.status_code == 403:
                print(" ⚠️  FORBIDDEN (no permission)")
            elif response.status_code == 404:
                print(" ❓ NOT FOUND")
            else:
                print(f" ❓ {response.status_code}")
                
        except Exception as e:
            print(f"{name:12} - ❌ Error: {e}")

if __name__ == "__main__":
    test_different_square_endpoints()
    check_token_permissions()
