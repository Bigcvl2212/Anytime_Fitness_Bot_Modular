#!/usr/bin/env python3
"""
Test different ClubOS API endpoints to find what works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clubos_integration_fixed import RobustClubOSClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_api_endpoints():
    """Test basic API endpoints to see what works"""
    
    # Load credentials
    try:
        from config.secrets_local import get_secret
        CLUBOS_USERNAME = get_secret("clubos-username")
        CLUBOS_PASSWORD = get_secret("clubos-password")
        
        if not CLUBOS_USERNAME or not CLUBOS_PASSWORD:
            print("❌ Could not load ClubOS credentials")
            return
    except ImportError:
        print("❌ Could not load credentials from config.secrets_local")
        return
    
    print("=== ClubOS API Endpoint Testing ===")
    
    # Initialize client with working authentication
    client = RobustClubOSClient(CLUBOS_USERNAME, CLUBOS_PASSWORD)
    
    # Authenticate
    print("🔐 Authenticating with ClubOS...")
    if not client.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful!")
    
    # Set loggedInUserId cookie for Jeremy Mayo
    client.session.cookies.set('loggedInUserId', '187032782', domain='.club-os.com')
    print("🍪 Set loggedInUserId cookie")
    
    # Test different API endpoints
    base_url = client.base_url
    
    # Test 1: Basic user info endpoint
    print("\n=== Testing User Info API ===")
    try:
        url = f"{base_url}/api/user/info"
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
            'Referer': f'{base_url}/action/Dashboard'
        }
        response = client.session.get(url, headers=headers)
        print(f"User Info API: {response.status_code}")
        if response.ok:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Calendar info without event IDs
    print("\n=== Testing Calendar API (no params) ===")
    try:
        url = f"{base_url}/api/calendar"
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
            'Referer': f'{base_url}/action/Calendar'
        }
        response = client.session.get(url, headers=headers)
        print(f"Calendar API (no params): {response.status_code}")
        if response.ok:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Calendar events with minimal params
    print("\n=== Testing Calendar Events API (minimal) ===")
    try:
        url = f"{base_url}/api/calendar/events"
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
            'Referer': f'{base_url}/action/Calendar'
        }
        # Try with just one event ID
        params = {
            'eventIds': '152438700',
            'fields': 'id'
        }
        response = client.session.get(url, headers=headers, params=params)
        print(f"Calendar Events API (minimal): {response.status_code}")
        if response.ok:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Try POST instead of GET
    print("\n=== Testing Calendar Events API (POST) ===")
    try:
        url = f"{base_url}/api/calendar/events"
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': f'{base_url}/action/Calendar'
        }
        data = {
            'eventIds': '152438700',
            'fields': 'id'
        }
        response = client.session.post(url, headers=headers, data=data)
        print(f"Calendar Events API (POST): {response.status_code}")
        if response.ok:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Check what form tokens we have
    print("\n=== Available Form Tokens ===")
    if hasattr(client, 'form_tokens'):
        for name, value in client.form_tokens.items():
            print(f"Token: {name} = {value[:20]}...")
    
    # Test 6: Check what cookies we have
    print("\n=== Available Cookies ===")
    for cookie in client.session.cookies:
        print(f"Cookie: {cookie.name} = {cookie.value[:20]}...")

if __name__ == "__main__":
    test_basic_api_endpoints()
