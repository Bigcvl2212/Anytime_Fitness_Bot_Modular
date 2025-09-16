#!/usr/bin/env python3
"""
Test Training Client Discovery - Small Sample

Test the ClubOS funding check on a few known members including Dennis
to verify the approach works before running on all 531 members.
"""

import sys
import os

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services'))

from api.clubhub_api_client import ClubHubAPIClient
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

# Import the training package cache (this has the ClubOS integration)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.services.training_package_cache import TrainingPackageCache
from src.clubos_training_api import ClubOSTrainingPackageAPI

def test_funding_check():
    print("=== TESTING TRAINING CLIENT DISCOVERY ===")
    print("Testing ClubOS funding check on known members")
    print()
    
    # Get a few members from ClubHub including Dennis
    print("🔐 Connecting to ClubHub...")
    client = ClubHubAPIClient()
    
    if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
        print("❌ ClubHub authentication failed")
        return
    
    print("✅ ClubHub authenticated")
    
    # Get first page of members
    members = client.get_all_members(page=1, page_size=100)
    print(f"📋 Got {len(members)} members from ClubHub")
    
    # Find Dennis and a few others to test
    test_members = []
    
    for member in members:
        name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
        
        # Add Dennis if found
        if 'DENNIS' in member.get('firstName', '').upper() and 'ROST' in member.get('lastName', '').upper():
            test_members.append(member)
            print(f"✅ Found Dennis Rost for testing")
        
        # Add a few others for comparison
        elif len(test_members) < 5:
            test_members.append(member)
    
    print(f"🧪 Testing {len(test_members)} members...")
    print()
    
    # Initialize the training package cache (this connects to ClubOS)
    cache = TrainingPackageCache()
    
    # Test each member
    for member in test_members:
        member_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
        member_email = member.get('email', '')
        
        print(f"🔍 Testing: {member_name}")
        
        try:
            # Use the existing funding lookup function
            funding_data = cache.lookup_participant_funding(member_name, member_email)
            
            if funding_data:
                print(f"   ✅ HAS TRAINING PACKAGE!")
                print(f"      Status: {funding_data.get('status_text', 'Unknown')}")
                print(f"      Payment: {funding_data.get('funding_status', 'Unknown')}")
                print(f"      Package: {funding_data.get('package_name', 'Unknown')}")
                print(f"      Sessions: {funding_data.get('sessions_remaining', 'Unknown')}")
                print()
            else:
                print(f"   ❌ No training package found")
                print()
                
        except Exception as e:
            print(f"   ⚠️ Error: {str(e)}")
            print()

if __name__ == "__main__":
    test_funding_check()
