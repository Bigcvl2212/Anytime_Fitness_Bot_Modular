#!/usr/bin/env python3
"""
Test the member category API endpoints directly to debug tab display issues
"""

import requests
import json
import os

def test_member_category_apis():
    """Test the member category API endpoints"""
    print("🔍 Testing member category API endpoints...")
    
    base_url = "http://localhost:5000"
    
    # Categories to test
    categories = ["yellow", "collections", "inactive"]
    
    for category in categories:
        print(f"\n=== Testing {category} category ===")
        
        try:
            url = f"{base_url}/api/members/by-category/{category}"
            print(f"URL: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    member_count = len(data.get('members', []))
                    print(f"✅ Success: {member_count} {category} members found")
                    
                    # Show first member as sample if any exist
                    if member_count > 0:
                        first_member = data['members'][0]
                        print(f"   Sample: {first_member.get('full_name', 'Unknown')} - {first_member.get('status_message', 'No status')}")
                    else:
                        print(f"   ⚠️  No {category} members returned")
                else:
                    print(f"❌ API Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error: Dashboard is not running at {base_url}")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_member_category_apis()