#!/usr/bin/env python3
"""
Debug Square Credentials - Check what's being used
"""
import os
import sys
sys.path.append('src')

from services.payments.square_client_simple import get_square_credentials, get_square_client
from config.secrets_local import get_secret

def debug_square_credentials():
    """Debug what Square credentials are being used"""
    print("🔍 Square Credentials Debug\n" + "="*50)
    
    # Check environment
    print(f"Environment Variable SQUARE_ENVIRONMENT: {os.getenv('SQUARE_ENVIRONMENT', 'Not Set')}")
    
    # Get credentials using our function
    creds = get_square_credentials()
    print(f"\n📋 Credentials Retrieved:")
    print(f"  - Environment: {creds.get('environment')}")
    print(f"  - Access Token: {creds.get('access_token', 'Not Set')[:20]}..." if creds.get('access_token') else "  - Access Token: Not Set")
    print(f"  - Location ID: {creds.get('location_id', 'Not Set')}")
    
    # Test individual secret lookups
    print(f"\n🔑 Direct Secret Lookups:")
    prod_token = get_secret("square-production-access-token")
    prod_location = get_secret("square-production-location-id")
    sandbox_token = get_secret("square-sandbox-access-token")
    sandbox_location = get_secret("square-sandbox-location-id")
    
    print(f"  - Production Token: {prod_token[:20] if prod_token else 'None'}...")
    print(f"  - Production Location: {prod_location}")
    print(f"  - Sandbox Token: {sandbox_token[:20] if sandbox_token else 'None'}...")
    print(f"  - Sandbox Location: {sandbox_location}")
    
    # Check if tokens look valid
    print(f"\n✅ Token Validation:")
    current_token = creds.get('access_token', '')
    if current_token:
        print(f"  - Token length: {len(current_token)} characters")
        print(f"  - Starts with 'EAAA': {'✅' if current_token.startswith('EAAA') else '❌'}")
        print(f"  - Environment: {creds.get('environment')}")
    else:
        print("  - ❌ No access token found")
        
    return creds

def test_square_auth():
    """Test Square API authentication"""
    print(f"\n🧪 Testing Square API Authentication:")
    
    client = get_square_client()
    if not client:
        print("❌ Could not create Square client")
        return
        
    try:
        # Try to list locations - this is a simple API call that should work if auth is good
        locations_api = client.locations
        result = locations_api.list()
        
        # If we get here without exception, it worked
        locations = result.locations if hasattr(result, 'locations') else []
        print(f"✅ Authentication successful!")
        print(f"   - Found {len(locations)} location(s)")
        for loc in locations[:3]:  # Show first 3
            loc_data = loc.__dict__ if hasattr(loc, '__dict__') else loc
            name = loc_data.get('name', 'Unknown') if isinstance(loc_data, dict) else getattr(loc, 'name', 'Unknown')
            loc_id = loc_data.get('id', 'No ID') if isinstance(loc_data, dict) else getattr(loc, 'id', 'No ID')
            print(f"   - Location: {name} ({loc_id})")
                
    except Exception as e:
        print(f"❌ Exception testing auth: {e}")
        
        # Try to extract useful error info
        if hasattr(e, 'body') and isinstance(e.body, dict):
            if 'errors' in e.body:
                for error in e.body['errors']:
                    print(f"   - Category: {error.get('category')}")
                    print(f"   - Code: {error.get('code')}")  
                    print(f"   - Detail: {error.get('detail')}")
        elif "401" in str(e):
            print("   - This is a 401 Unauthorized error - token is still invalid")

if __name__ == "__main__":
    creds = debug_square_credentials()
    if creds and creds.get('access_token'):
        test_square_auth()
    else:
        print("\n❌ No valid credentials found - skipping API test")
