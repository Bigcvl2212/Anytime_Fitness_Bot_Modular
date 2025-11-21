#!/usr/bin/env python3
"""
Quickly unlock Timothy Greuel using existing unlock method
"""

import sqlite3
from src.services.member_access_control import MemberAccessControl

def unlock_timothy_greuel():
    conn = sqlite3.connect('gym_bot.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print('🔓 === Unlocking Timothy Greuel ===')
    
    # Get Timothy Greuel's data
    cursor.execute('''
    SELECT * FROM members WHERE prospect_id = ?
    ''', ('63235560',))
    
    member = cursor.fetchone()
    
    if not member:
        print('❌ Timothy Greuel not found')
        conn.close()
        return
    
    print(f'Found: {member["full_name"]} (ID: {member["prospect_id"]})')
    
    # Create member access control instance
    access_control = MemberAccessControl(user_email="Manual Unlock - Admin")
    
    # Prepare member data for unlocking
    member_data = {
        'prospect_id': member["prospect_id"],
        'display_name': member["full_name"],
        'status_message': member["status_message"],
        'full_name': member["full_name"]
    }
    
    print(f'🔓 Attempting to unlock Timothy Greuel...')
    
    try:
        result = access_control._unlock_member(member_data)
        
        if result['success']:
            print(f'✅ Successfully unlocked Timothy Greuel')
            print(f'   Result: {result}')
            
            # Test access immediately
            print(f'\n🧪 Testing access after unlock...')
            
            # Import what we need for testing
            from src.services.authentication.secure_secrets_manager import SecureSecretsManager
            from src.services.api.clubhub_api_client import ClubHubAPIClient
            from datetime import datetime
            
            secrets_manager = SecureSecretsManager()
            email = secrets_manager.get_secret("clubhub-email")
            password = secrets_manager.get_secret("clubhub-password")
            
            client = ClubHubAPIClient()
            auth_success = client.authenticate(email, password)
            
            if auth_success:
                checkin_data = {
                    "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S-05:00"),
                    "door": {"id": 772},
                    "club": {"id": 1156},
                    "manual": True
                }
                
                access_result = client.post_member_usage('63235560', checkin_data)
                
                if access_result and access_result.get('admitted'):
                    print(f'✅ SUCCESS: Member can now check in after unlock!')
                    print(f'   Access result: admitted = {access_result.get("admitted")}')
                else:
                    print(f'❌ Member still cannot access after unlock')
                    print(f'   Access result: {access_result}')
            else:
                print(f'❌ Could not test access - authentication failed')
        else:
            print(f'❌ Failed to unlock Timothy Greuel: {result.get("error", "Unknown error")}')
            
    except Exception as e:
        print(f'❌ Error during unlock process: {e}')
    
    conn.close()

if __name__ == "__main__":
    unlock_timothy_greuel()