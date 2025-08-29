#!/usr/bin/env python3
"""
Test Square API with raw HTTP requests to debug authentication
"""
import requests
import json
import os
import sys
sys.path.append('src')

from config.secrets_local import get_secret

def test_raw_square_api():
    """Test Square API with raw HTTP requests"""
    print("🌐 RAW SQUARE API TEST")
    print("=" * 50)
    
    # Get production credentials
    prod_token = get_secret("square-production-access-token")
    prod_location = get_secret("square-production-location-id")
    
    print(f"Using token: {prod_token[:20]}...")
    print(f"Using location: {prod_location}")
    
    # Test with production environment
    headers = {
        'Authorization': f'Bearer {prod_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Square-Version': '2024-07-17',  # Latest API version
        'User-Agent': 'Anytime-Fitness-Bot/1.0'
    }
    
    print(f"\n📡 Headers being sent:")
    for key, value in headers.items():
        if key == 'Authorization':
            print(f"  {key}: Bearer {value[7:27]}...")
        else:
            print(f"  {key}: {value}")
    
    # Test locations endpoint
    print(f"\n🎯 Testing Locations API (Production)...")
    try:
        response = requests.get(
            'https://connect.squareup.com/v2/locations',
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            locations = data.get('locations', [])
            print(f"✅ Success! Found {len(locations)} locations")
            for loc in locations[:2]:
                print(f"  - {loc.get('name', 'Unknown')} ({loc.get('id', 'No ID')})")
        else:
            print(f"❌ Error Response:")
            try:
                error_data = response.json()
                print(f"   {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw response: {response.text}")
                
    except Exception as e:
        print(f"❌ Request exception: {e}")
    
    # Test with sandbox
    print(f"\n🎯 Testing Locations API (Sandbox)...")
    sandbox_token = get_secret("square-sandbox-access-token")
    sandbox_headers = headers.copy()
    sandbox_headers['Authorization'] = f'Bearer {sandbox_token}'
    
    try:
        response = requests.get(
            'https://connect.squareupsandbox.com/v2/locations',
            headers=sandbox_headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            locations = data.get('locations', [])
            print(f"✅ Sandbox Success! Found {len(locations)} locations")
            for loc in locations[:2]:
                print(f"  - {loc.get('name', 'Unknown')} ({loc.get('id', 'No ID')})")
        else:
            print(f"❌ Sandbox Error Response:")
            try:
                error_data = response.json()
                print(f"   {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw response: {response.text}")
                
    except Exception as e:
        print(f"❌ Sandbox request exception: {e}")

def test_square_application_info():
    """Test if we can get application info"""
    print(f"\n🔍 TESTING APPLICATION INFO...")
    
    prod_token = get_secret("square-production-access-token")
    headers = {
        'Authorization': f'Bearer {prod_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Square-Version': '2024-07-17'
    }
    
    try:
        # Try to get merchant info
        response = requests.get(
            'https://connect.squareup.com/v2/merchants',
            headers=headers,
            timeout=30
        )
        
        print(f"Merchants endpoint - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            merchants = data.get('merchants', [])
            print(f"✅ Found {len(merchants)} merchants")
            for merchant in merchants[:1]:
                print(f"  - Business Name: {merchant.get('business_name', 'Unknown')}")
                print(f"  - Country: {merchant.get('country', 'Unknown')}")
                print(f"  - Status: {merchant.get('status', 'Unknown')}")
        else:
            error_data = response.json()
            print(f"❌ Merchants error: {error_data}")
            
    except Exception as e:
        print(f"❌ Merchants request exception: {e}")

if __name__ == "__main__":
    test_raw_square_api()
    test_square_application_info()
