#!/usr/bin/env python3
"""
Test the member category frontend fixes by checking the HTML structure
"""

import requests
from bs4 import BeautifulSoup

def test_member_category_tabs():
    """Test that the member category tabs have proper HTML structure"""
    print("🔍 Testing member category tab structure...")
    
    try:
        # Get the members page HTML
        response = requests.get("http://localhost:5000/members", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed to get members page: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Test categories that were having issues
        categories = [
            ("yellow", "yellow-members", "yellow-members-container"),
            ("collections", "collections-members", "collections-members-container"), 
            ("inactive", "inactive-members", "inactive-members-container")
        ]
        
        print("\n=== TAB STRUCTURE TESTS ===")
        
        for category, tab_id, container_id in categories:
            print(f"\n--- Testing {category} category ---")
            
            # Check if tab button exists
            tab_button = soup.find("button", {"id": f"{category}-members-tab"}) or soup.find("button", {"id": f"{category}-tab"})
            if tab_button:
                print(f"✅ Tab button found for {category}")
                target = tab_button.get("data-bs-target", "")
                print(f"   Target: {target}")
            else:
                print(f"❌ Tab button NOT found for {category}")
                
            # Check if tab pane exists
            tab_pane = soup.find("div", {"id": tab_id})
            if tab_pane:
                print(f"✅ Tab pane found: #{tab_id}")
            else:
                print(f"❌ Tab pane NOT found: #{tab_id}")
                
            # Check if container exists
            container = soup.find("div", {"id": container_id})
            if container:
                print(f"✅ Container found: #{container_id}")
            else:
                print(f"❌ Container NOT found: #{container_id}")
        
        print("\n=== API ENDPOINT TESTS ===")
        
        # Test that each category API returns data
        for category, _, _ in categories:
            try:
                api_url = f"http://localhost:5000/api/members/by-category/{category}"
                api_response = requests.get(api_url, timeout=5)
                
                if api_response.status_code == 200:
                    data = api_response.json()
                    if data.get('success'):
                        member_count = len(data.get('members', []))
                        print(f"✅ {category} API: {member_count} members")
                    else:
                        print(f"❌ {category} API error: {data.get('error')}")
                else:
                    print(f"❌ {category} API HTTP error: {api_response.status_code}")
                    
            except Exception as e:
                print(f"❌ {category} API exception: {e}")
        
        print("\n=== SUMMARY ===")
        print("If all tests pass with ✅, the member category tabs should be working!")
        print("If any tests fail with ❌, those issues need to be fixed.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Dashboard is not running at http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_member_category_tabs()