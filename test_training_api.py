#!/usr/bin/env python3
"""
Test script to verify ClubOS training API functionality
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from clubos_training_api_fixed import ClubOSTrainingPackageAPI
    print("✅ ClubOS Training API imported successfully")
    
    # Create API instance
    api = ClubOSTrainingPackageAPI()
    print(f"✅ API instance created, username: {api.username}, password: {'*' * len(api.password) if api.password else 'None'}")
    
    # Set credentials manually
    api.username = "j.mayo"
    api.password = "j@SD4fjhANK5WNA"
    print(f"✅ Credentials set, username: {api.username}, password: {'*' * len(api.password) if api.password else 'None'}")
    
    # Try to authenticate
    print("🔐 Attempting authentication...")
    auth_result = api.authenticate()
    print(f"✅ Authentication result: {auth_result}")
    print(f"✅ Authenticated: {api.authenticated}")
    
    if auth_result:
        # Try to fetch assignees
        print("📋 Fetching assignees...")
        assignees = api.fetch_assignees()
        print(f"✅ Assignees fetched: {len(assignees) if assignees else 0}")
        
        if assignees and len(assignees) > 0:
            # Try to get payment details for the first assignee
            first_assignee = assignees[0]
            member_id = first_assignee.get('id')
            print(f"🔍 Testing payment details for member: {member_id}")
            
            if member_id:
                payment_details = api.get_member_training_payment_details(member_id)
                print(f"✅ Payment details: {payment_details}")
            else:
                print("⚠️ No member ID found in first assignee")
        else:
            print("⚠️ No assignees found")
    else:
        print("❌ Authentication failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
