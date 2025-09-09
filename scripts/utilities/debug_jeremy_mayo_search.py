#!/usr/bin/env python3
"""
Debug script to print raw search results for Jeremy Mayo
"""

from config.secrets_local import get_secret
from src.services.api.clubos_api_client import ClubOSAPIClient

def debug_jeremy_mayo_search():
    """Debug the search results for Jeremy Mayo"""
    
    print("🔍 Debugging Jeremy Mayo search...")
    print("=" * 50)
    
    # Create API client and authenticate
    client = ClubOSAPIClient()
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    print("1. Authenticating...")
    if not client.auth.login(username, password):
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Search for Jeremy Mayo
    print("\n2. Searching for Jeremy Mayo...")
    results = client.search_members("Jeremy Mayo")
    
    print(f"\n3. Raw search results:")
    print(f"   Type: {type(results)}")
    print(f"   Length: {len(results) if isinstance(results, list) else 'N/A'}")
    
    if isinstance(results, list):
        print(f"\n4. Found {len(results)} results:")
        for i, result in enumerate(results):
            print(f"\n   Result {i+1}:")
            print(f"   Type: {type(result)}")
            if isinstance(result, dict):
                for key, value in result.items():
                    print(f"   {key}: {value}")
            else:
                print(f"   Value: {result}")
    
    # Try to find Jeremy Mayo specifically
    print(f"\n5. Looking for Jeremy Mayo specifically...")
    jeremy_found = False
    if isinstance(results, list):
        for result in results:
            if isinstance(result, dict):
                # Check various name fields
                name_fields = ['name', 'full_name', 'member_name', 'display_name', 'firstName', 'lastName']
                for field in name_fields:
                    if field in result:
                        name_value = str(result[field]).lower()
                        if 'jeremy' in name_value and 'mayo' in name_value:
                            print(f"   ✅ Found Jeremy Mayo in field '{field}': {result[field]}")
                            print(f"   Full result: {result}")
                            jeremy_found = True
                            break
                if jeremy_found:
                    break
    
    if not jeremy_found:
        print("   ❌ Jeremy Mayo not found in search results")
        
        # Print all names to see what we got
        print(f"\n6. All names found:")
        if isinstance(results, list):
            for result in results:
                if isinstance(result, dict):
                    for field in ['name', 'full_name', 'member_name', 'display_name', 'firstName', 'lastName']:
                        if field in result:
                            print(f"   {result[field]}")

if __name__ == "__main__":
    debug_jeremy_mayo_search() 