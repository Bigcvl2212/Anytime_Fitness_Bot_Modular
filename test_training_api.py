#!/usr/bin/env python3
"""
Test script to debug ClubOS Training API
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from clubos_training_api import ClubOSTrainingPackageAPI

def test_training_api():
    print("🔐 Testing ClubOS Training API...")
    
    # Initialize API
    api = ClubOSTrainingPackageAPI()
    
    # Test authentication
    print("🔑 Attempting authentication...")
    if api.authenticate():
        print("✅ Authentication successful!")
        print(f"🔗 Base URL: {api.base_url}")
        print(f"🔑 Authenticated: {api.authenticated}")
        
        # Test fetching assignees
        print("📋 Fetching assignees...")
        assignees = api.fetch_assignees(force_refresh=True)
        
        if assignees:
            print(f"✅ Found {len(assignees)} training clients:")
            for i, client in enumerate(assignees[:5]):  # Show first 5
                print(f"  {i+1}. {client.get('name', 'Unknown')} (ID: {client.get('id', 'Unknown')})")
        else:
            print("❌ No assignees found")
            
    else:
        print("❌ Authentication failed!")
        print(f"🔑 Username: {api.username}")
        print(f"🔑 Password: {'*' * len(api.password) if api.password else 'None'}")

if __name__ == "__main__":
    test_training_api()
