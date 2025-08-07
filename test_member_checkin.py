#!/usr/bin/env python3
"""
Test member check-in for Member ID 1 (e.colinjr@gmail.com)
"""

import sys
import os
sys.path.append('.')

from member_retention_system import MemberRetentionSystem
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_member_checkin():
    """Test checking in Member ID 1"""
    
    print("🏋️ Testing Member Check-in System")
    print("=" * 40)
    print("Member: ID 1 (e.colinjr@gmail.com)")
    print()
    
    # Initialize the retention system
    retention_system = MemberRetentionSystem()
    
    # You'll need to provide a ClubHub auth token
    # This is the Bearer token from the ClubHub API calls
    auth_token = input("Enter ClubHub Bearer token: ").strip()
    
    if not auth_token:
        print("❌ No auth token provided. Cannot proceed.")
        return
    
    # Set the auth token
    retention_system.set_auth_token(auth_token)
    
    # Test checking in Member ID 1
    member_id = "1"  # Using the database member ID as ClubHub member ID
    
    print(f"🔄 Attempting to check in Member ID {member_id}...")
    
    # Perform the check-in
    success = retention_system.manual_checkin_member(member_id)
    
    if success:
        print("✅ Check-in successful!")
        print("🎉 Member retention system is working!")
    else:
        print("❌ Check-in failed. Check the logs for details.")
        print("💡 This could be due to:")
        print("   - Invalid member ID")
        print("   - Expired auth token")
        print("   - API rate limiting")
        print("   - Network issues")

if __name__ == "__main__":
    test_member_checkin()
