#!/usr/bin/env python3
"""
Find Jeremy Mayo in ClubOS using the correct location ID from HAR file
"""

from services.api.clubos_api_client import ClubOSAPIClient
from config.secrets_local import get_secret
import json

def find_jeremy_mayo_clubos():
    """Search for Jeremy Mayo in ClubOS using the correct location ID"""
    
    print("🔍 Searching for Jeremy Mayo in ClubOS...")
    print("=" * 60)
    
    # Create API client and authenticate
    client = ClubOSAPIClient()
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    print("1. Authenticating with ClubOS...")
    if not client.auth.login(username, password):
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Search for Jeremy Mayo using different search queries
    search_queries = [
        "Jeremy Mayo",
        "Jeremy",
        "Mayo", 
        "j.mayo",
        "jmayo",
        "jeremy.mayo",
        "jeremymayo"
    ]
    
    jeremy_found = False
    
    for query in search_queries:
        print(f"\n2. Searching for: '{query}'")
        print("-" * 40)
        
        try:
            # Use the UserSearch endpoint discovered in HAR
            headers = client.auth.get_headers()
            
            # Try the UserSearch endpoint with different parameters
            search_params = [
                {"q": query},
                {"search": query},
                {"member_name": query},
                {"query": query}
            ]
            
            for params in search_params:
                try:
                    response = client.auth.session.get(
                        f"{client.base_url}/action/UserSearch",
                        params=params,
                        headers=headers,
                        timeout=30,
                        verify=False
                    )
                    
                    print(f"   Status: {response.status_code}")
                    print(f"   URL: {response.url}")
                    
                    if response.status_code == 200:
                        print(f"   ✅ Search successful for '{query}'")
                        
                        # Parse the HTML response
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Look for Jeremy Mayo in the response
                        text_content = soup.get_text().lower()
                        if 'jeremy' in text_content and 'mayo' in text_content:
                            print(f"   🎯 Found 'Jeremy Mayo' in response!")
                            jeremy_found = True
                            
                            # Try to extract member information
                            print(f"   📄 Response preview:")
                            print(f"   {response.text[:500]}...")
                            
                            # Look for member IDs in the HTML
                            import re
                            member_id_patterns = [
                                r'data-member-id="(\d+)"',
                                r'data-user-id="(\d+)"',
                                r'data-id="(\d+)"',
                                r'member_id=(\d+)',
                                r'user_id=(\d+)'
                            ]
                            
                            for pattern in member_id_patterns:
                                matches = re.findall(pattern, response.text)
                                if matches:
                                    print(f"   🔑 Found potential member IDs: {matches}")
                        
                        break
                        
                except Exception as e:
                    print(f"   ⚠️ Search attempt failed: {e}")
                    continue
            
            if jeremy_found:
                break
                
        except Exception as e:
            print(f"   ❌ Search error: {e}")
            continue
    
    # Also try the UserSuggest endpoint
    print(f"\n3. Trying UserSuggest endpoint...")
    try:
        response = client.auth.session.get(
            f"{client.base_url}/action/UserSuggest/global/",
            params={"q": "Jeremy Mayo"},
            headers=headers,
            timeout=30,
            verify=False
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ UserSuggest successful")
            print(f"   📄 Response: {response.text[:200]}...")
            
            # Check if Jeremy Mayo is in the response
            if 'jeremy' in response.text.lower() and 'mayo' in response.text.lower():
                print(f"   🎯 Found 'Jeremy Mayo' in UserSuggest response!")
                jeremy_found = True
    
    except Exception as e:
        print(f"   ❌ UserSuggest error: {e}")
    
    # Try to get member details if we found any IDs
    if jeremy_found:
        print(f"\n4. Attempting to get member details...")
        # This would require the actual member ID from the search results
        print(f"   ℹ️ Member details would be retrieved here with the found member ID")
    
    if not jeremy_found:
        print(f"\n❌ Jeremy Mayo not found in ClubOS searches")
        print(f"   This could mean:")
        print(f"   - You're not a member at this ClubOS location")
        print(f"   - Your name is recorded differently in the system")
        print(f"   - You're at a different gym location")
    
    return jeremy_found

if __name__ == "__main__":
    find_jeremy_mayo_clubos() 