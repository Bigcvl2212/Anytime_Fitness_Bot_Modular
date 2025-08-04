#!/usr/bin/env python3
"""
Test ClubOS API with form tokens as headers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clubos_integration_fixed import RobustClubOSClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_api_with_form_tokens():
    """Test API endpoints with form tokens as headers"""
    
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
    
    print("=== ClubOS API with Form Tokens Test ===")
    
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
    
    # Print available tokens
    print("\n=== Available Form Tokens ===")
    if hasattr(client, 'form_tokens'):
        for name, value in client.form_tokens.items():
            print(f"Token: {name} = {value[:20]}...")
    
    # Prepare headers with form tokens
    base_headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': f'{client.base_url}/action/Calendar'
    }
    
    # Add form tokens as headers
    if hasattr(client, 'form_tokens'):
        for name, value in client.form_tokens.items():
            if name in ['__fp', '_sourcePage']:
                base_headers[f'X-{name}'] = value
                print(f"Added header: X-{name}")
    
    # Add CSRF token if available
    if hasattr(client, 'csrf_token') and client.csrf_token:
        base_headers['X-CSRF-Token'] = client.csrf_token
        print("Added CSRF token header")
    
    # Test Calendar Events API with form token headers
    print("\n=== Testing Calendar Events API with Form Tokens ===")
    try:
        url = f"{client.base_url}/api/calendar/events"
        
        # Try as form data instead of query parameters
        data = {
            'eventIds': '152438700',
            'fields': 'id,fundingStatus',
        }
        
        # Add form tokens to the data as well
        if hasattr(client, 'form_tokens'):
            for name, value in client.form_tokens.items():
                if name in ['__fp', '_sourcePage']:
                    data[name] = value
        
        print(f"Request URL: {url}")
        print(f"Request Headers: {base_headers}")
        print(f"Request Data: {data}")
        
        response = client.session.post(url, headers=base_headers, data=data)
        print(f"Calendar Events API (POST with tokens): {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        if response.ok:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with GET and form tokens in headers only
    print("\n=== Testing Calendar Events API (GET with token headers) ===")
    try:
        url = f"{client.base_url}/api/calendar/events"
        params = {
            'eventIds': '152438700',
            'fields': 'id,fundingStatus',
        }
        
        response = client.session.get(url, headers=base_headers, params=params)
        print(f"Calendar Events API (GET with token headers): {response.status_code}")
        if response.ok:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test a different endpoint pattern - maybe the calendar page has embedded data
    print("\n=== Testing Calendar Page for Embedded Data ===")
    try:
        url = f"{client.base_url}/action/Calendar"
        response = client.session.get(url)
        
        if response.ok:
            # Look for JSON data in the HTML
            import re
            json_matches = re.findall(r'(?:events|calendar).*?(\{.*?\})', response.text, re.IGNORECASE | re.DOTALL)
            if json_matches:
                print("Found potential JSON data in calendar page:")
                for i, match in enumerate(json_matches[:3]):  # Show first 3 matches
                    print(f"Match {i+1}: {match[:100]}...")
            else:
                print("No JSON data found in calendar page")
                
            # Look for API endpoints in JavaScript
            api_matches = re.findall(r'(?:api|endpoint).*?["\']([^"\']+)["\']', response.text, re.IGNORECASE)
            if api_matches:
                print("Found potential API endpoints:")
                for endpoint in set(api_matches[:10]):  # Show unique endpoints
                    print(f"  {endpoint}")
        else:
            print(f"Failed to load calendar page: {response.status_code}")
    except Exception as e:
        print(f"Error analyzing calendar page: {e}")

if __name__ == "__main__":
    test_api_with_form_tokens()
