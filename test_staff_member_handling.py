#!/usr/bin/env python3
"""
Test staff member handling in access control
"""

from src.services.member_access_control import MemberAccessControl

def test_staff_member_handling():
    print('🧪 === Testing Staff Member Access Control ===')
    
    # Create member access control instance
    access_control = MemberAccessControl(user_email="test@gym.com")
    
    # Mock staff member data (like member 52750389)
    staff_member = {
        'prospect_id': '52750389',
        'display_name': 'JOSEPH JONES',
        'status_message': 'Member is in good standing, Staff Member',
        'full_name': 'JOSEPH JONES'
    }
    
    print(f'Testing with staff member: {staff_member["display_name"]}')
    print(f'Status: {staff_member["status_message"]}')
    
    # Test lock operation
    print(f'\n🔒 Testing lock operation...')
    lock_result = access_control._lock_member(staff_member)
    print(f'Lock result: {lock_result}')
    
    # Test unlock operation
    print(f'\n🔓 Testing unlock operation...')
    unlock_result = access_control._unlock_member(staff_member)
    print(f'Unlock result: {unlock_result}')
    
    # Test with regular member for comparison
    print(f'\n📋 Testing with regular past due member...')
    regular_member = {
        'prospect_id': '12345678',
        'display_name': 'JOHN DOE',
        'status_message': 'Member Account is Past Due',
        'full_name': 'JOHN DOE'
    }
    
    print(f'Testing with regular member: {regular_member["display_name"]}')
    print(f'Status: {regular_member["status_message"]}')
    
    lock_result = access_control._lock_member(regular_member)
    print(f'Regular member lock result: {lock_result}')

if __name__ == "__main__":
    test_staff_member_handling()