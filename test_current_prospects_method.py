#!/usr/bin/env python3
"""
Test the exact current prospects method that clean_dashboard uses
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.api.clubhub_api_client import ClubHubAPIClient

def test_current_prospects():
    """Test exactly what clean_dashboard.py is doing"""
    print("🔄 Testing current prospects method from clean_dashboard.py...")
    
    # Initialize the client exactly as clean_dashboard does
    client = ClubHubAPIClient()
    
    # Call the exact same method that clean_dashboard uses
    print("🔍 Calling get_all_prospects_paginated()...")
    all_prospects = client.get_all_prospects_paginated()
    
    print(f"✅ Retrieved {len(all_prospects)} prospects from ClubHub")
    
    if all_prospects:
        print(f"📋 First prospect: {all_prospects[0].get('firstName', '')} {all_prospects[0].get('lastName', '')} - {all_prospects[0].get('email', 'No email')}")
        print(f"📋 Sample prospect keys: {list(all_prospects[0].keys())}")
    
    # Save results
    import json
    with open("current_prospects_test.json", "w") as f:
        json.dump(all_prospects, f, indent=2)
    
    print(f"💾 Saved {len(all_prospects)} prospects to current_prospects_test.json")

if __name__ == "__main__":
    test_current_prospects()
