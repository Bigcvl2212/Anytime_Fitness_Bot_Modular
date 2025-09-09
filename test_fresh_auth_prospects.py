#!/usr/bin/env python3
"""
Test prospects with fresh authentication
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.api.clubhub_api_client import ClubHubAPIClient
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

def test_with_fresh_auth():
    """Test prospects with fresh authentication"""
    print("🔄 Testing prospects with fresh authentication...")
    
    # Initialize the client
    client = ClubHubAPIClient()
    
    # First, try to authenticate with fresh credentials
    print("🔐 Attempting authentication...")
    auth_result = client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD)
    
    if not auth_result:
        print("❌ Authentication failed!")
        return
    
    print("✅ Authentication successful!")
    
    # Now try to get prospects
    print("🔍 Calling get_all_prospects_paginated()...")
    all_prospects = client.get_all_prospects_paginated()
    
    print(f"🎉 Retrieved {len(all_prospects)} prospects from ClubHub")
    
    if all_prospects:
        print(f"📋 First prospect: {all_prospects[0].get('firstName', '')} {all_prospects[0].get('lastName', '')} - {all_prospects[0].get('email', 'No email')}")
        print(f"📋 Sample prospect keys: {list(all_prospects[0].keys())}")
    
    # Save results
    import json
    with open("fresh_auth_prospects.json", "w") as f:
        json.dump(all_prospects, f, indent=2)
    
    print(f"💾 Saved {len(all_prospects)} prospects to fresh_auth_prospects.json")
    
    return len(all_prospects)

if __name__ == "__main__":
    test_with_fresh_auth()
