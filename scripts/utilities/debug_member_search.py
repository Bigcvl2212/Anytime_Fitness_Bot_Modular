#!/usr/bin/env python3
"""
Debug ClubOS Member Search - Show Raw Results
"""

from src.services.api.clubos_api_client import ClubOSAPIClient
import json

def debug_search_results():
    """Debug the member search to see exactly what ClubOS returns"""
    
    print("🔍 DEBUG: Searching for Jeremy Mayo in ClubOS")
    print("=" * 60)
    
    client = ClubOSAPIClient()
    if not client.authenticate():
        print("❌ Authentication failed")
        return
    
    # Test different search queries
    search_queries = ["Jeremy Mayo", "Jeremy", "Mayo", "j.mayo", "jmayo"]
    
    for query in search_queries:
        print(f"\n🔍 Searching for: '{query}'")
        print("-" * 40)
        
        try:
            # Get raw response from the search endpoint
            headers = client.auth.get_headers()
            
            # Try the UserSearch endpoint
            response = client.auth.session.get(
                f"{client.base_url}/action/UserSearch",
                params={"q": query},
                headers=headers,
                timeout=30,
                verify=False
            )
            
            print(f"Status: {response.status_code}")
            print(f"URL: {response.url}")
            print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            if response.ok:
                # Show first 500 chars of response
                content = response.text
                print(f"Response length: {len(content)} characters")
                print(f"First 500 chars: {content[:500]}")
                
                # Try to parse as JSON if possible
                try:
                    json_data = response.json()
                    print(f"JSON Response: {json.dumps(json_data, indent=2)[:1000]}")
                except:
                    print("Not JSON - showing as HTML/text")
                
                # Look for any member-related content
                if "jeremy" in content.lower() or "mayo" in content.lower():
                    print("🎯 FOUND: Your name appears in the response!")
                else:
                    print("❌ Your name not found in response")
                    
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Also test the UserSuggest endpoint
    print(f"\n🔍 Testing UserSuggest endpoint...")
    try:
        response = client.auth.session.get(
            f"{client.base_url}/action/UserSuggest/global/",
            params={"q": "Jeremy Mayo"},
            headers=headers,
            timeout=30,
            verify=False
        )
        
        print(f"UserSuggest Status: {response.status_code}")
        if response.ok:
            print(f"UserSuggest Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"UserSuggest Error: {e}")

if __name__ == "__main__":
    debug_search_results() 