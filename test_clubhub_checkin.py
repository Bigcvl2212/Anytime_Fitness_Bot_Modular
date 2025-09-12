#!/usr/bin/env python3
"""
Simple test script to check in a member using ClubHub API member lookup
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.api.clubhub_api_client import ClubHubAPIClient
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_member_checkin():
    """Test checking in a member by finding them in ClubHub"""
    
    print("🏋️ Testing ClubHub Member Check-in")
    print("=" * 40)
    
    # Initialize and authenticate
    client = ClubHubAPIClient()
    
    if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
        print("❌ Authentication failed")
        return
    
    # Get some members from ClubHub API
    print("\n🔍 Getting members from ClubHub...")
    
    try:
        # Get members from ClubHub API
        members_response = client.get_all_members(page=1, page_size=10)
        
        if members_response and isinstance(members_response, list):
            members = members_response
            print(f"📋 Found {len(members)} members")
            
            # Show first few members
            print("👥 Sample members:")
            for i, member in enumerate(members[:3]):
                member_id = member.get('id')
                first_name = member.get('firstName', 'Unknown')
                last_name = member.get('lastName', 'Unknown') 
                email = member.get('email', 'No email')
                print(f"   {i+1}. ID: {member_id} | {first_name} {last_name} | {email}")
            
            # Try to check in the first member
            if members:
                test_member = members[0]
                member_id = test_member.get('id')
                member_name = f"{test_member.get('firstName', '')} {test_member.get('lastName', '')}"
                
                print(f"\n🔄 Testing check-in for: {member_name} (ID: {member_id})")
                
                from datetime import datetime
                checkin_data = {
                    "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S-05:00"),
                    "door": {"id": 772},
                    "club": {"id": 1156},
                    "manual": True
                }
                
                result = client.post_member_usage(str(member_id), checkin_data)
                
                if result:
                    print("✅ Check-in successful!")
                    print(f"Response: {result}")
                else:
                    print("❌ Check-in failed")
        else:
            print("❌ Unexpected response format")
            print(f"Response type: {type(members_response)}")
            print(f"Response: {members_response}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.exception("Full error details:")

if __name__ == "__main__":
    test_member_checkin()
