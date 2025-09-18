#!/usr/bin/env python3
"""
Find and ban Timothy Greuel
"""

import sqlite3
from src.services.member_access_control import MemberAccessControl

def find_and_ban_timothy_greuel():
    conn = sqlite3.connect('gym_bot.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print('🔍 === Finding Timothy Greuel ===')
    
    # Search for Timothy Greuel (try various name formats)
    cursor.execute('''
    SELECT * FROM members 
    WHERE LOWER(full_name) LIKE '%timothy%greuel%' 
       OR LOWER(full_name) LIKE '%greuel%timothy%'
       OR LOWER(first_name) LIKE '%timothy%' AND LOWER(last_name) LIKE '%greuel%'
    ''')
    
    members = cursor.fetchall()
    
    if not members:
        print('❌ Timothy Greuel not found in database')
        conn.close()
        return
    
    if len(members) > 1:
        print(f'⚠️  Multiple matches found for Timothy Greuel:')
        for i, member in enumerate(members, 1):
            print(f'  {i}. ID: {member["prospect_id"]} | Name: {member["full_name"]} | Status: {member["status_message"]}')
        
        # Use the first match or let user choose
        member = members[0]
        print(f'\n🎯 Using first match: {member["full_name"]} (ID: {member["prospect_id"]})')
    else:
        member = members[0]
        print(f'✅ Found Timothy Greuel: {member["full_name"]} (ID: {member["prospect_id"]})')
    
    print(f'\n📋 Member Details:')
    print(f'  ID: {member["prospect_id"]}')
    print(f'  Name: {member["full_name"]}')
    print(f'  Status Message: {member["status_message"]}')
    print(f'  Member Type: {member["member_type"]}')
    print(f'  User Type: {member["user_type"]}')
    
    # Check if this is a staff member or has special status
    status_message = member["status_message"] or ''
    if 'Staff' in status_message:
        print(f'\n⚠️  WARNING: This appears to be a Staff member!')
        print(f'   Staff members typically cannot be banned through normal processes.')
        conn.close()
        return
    elif 'Pay Per Visit' in status_message:
        print(f'\n⚠️  WARNING: This is a Pay Per Visit member!')
        print(f'   PPV members should not be banned.')
        conn.close()
        return
    
    # Create member access control instance
    print(f'\n🔒 === Attempting to Ban Timothy Greuel ===')
    access_control = MemberAccessControl(user_email="Manual Request - Admin")
    
    # Prepare member data for banning
    member_data = {
        'prospect_id': member["prospect_id"],
        'display_name': member["full_name"],
        'status_message': member["status_message"],
        'full_name': member["full_name"]
    }
    
    # Attempt to ban the member
    try:
        result = access_control._lock_member(member_data)
        
        if result['success']:
            if result.get('action') == 'skipped_staff':
                print(f'⚠️  Member skipped: {result["message"]}')
            elif result.get('was_already_locked'):
                print(f'✅ Member was already banned')
            else:
                print(f'✅ Successfully banned Timothy Greuel (ID: {member["prospect_id"]})')
                print(f'   Ban result: {result}')
        else:
            print(f'❌ Failed to ban Timothy Greuel: {result.get("error", "Unknown error")}')
            
    except Exception as e:
        print(f'❌ Error during ban process: {e}')
    
    conn.close()

if __name__ == "__main__":
    find_and_ban_timothy_greuel()