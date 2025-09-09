#!/usr/bin/env python3
"""
ClubOS Member ID Diagnostic Tool
Tests if our member IDs actually exist in ClubOS
"""

import requests
import logging
from bs4 import BeautifulSoup

def test_member_ids():
    """Test if our member IDs are valid in ClubOS"""
    
    # Sample member IDs from our recent campaign
    test_member_ids = ["7036735", "26047839", "343061"]
    
    print("🔍 Testing ClubOS Member ID Validation...")
    print("=" * 50)
    
    # You would need to authenticate first, then test each ID
    session = requests.Session()
    
    for member_id in test_member_ids:
        try:
            # Test if member profile loads
            profile_url = f"https://anytime.club-os.com/action/Dashboard/member/{member_id}"
            
            print(f"\n📋 Testing Member ID: {member_id}")
            print(f"   Profile URL: {profile_url}")
            
            # This would require authentication first
            # response = session.get(profile_url)
            # if response.status_code == 200:
            #     print(f"   ✅ Member exists and accessible")
            # else:
            #     print(f"   ❌ Member not found or not accessible ({response.status_code})")
            
            print(f"   ⚠️ Test requires ClubOS authentication")
            
        except Exception as e:
            print(f"   ❌ Error testing member {member_id}: {e}")

if __name__ == "__main__":
    test_member_ids()
