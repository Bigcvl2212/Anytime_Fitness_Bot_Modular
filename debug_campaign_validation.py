#!/usr/bin/env python3
"""
Debug Campaign Validation Pipeline
Trace exactly where members are being filtered out during campaign processing
"""

import os
import sys
import sqlite3
import json
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_campaign_validation():
    """Debug the exact campaign validation pipeline without sending campaigns"""
    
    print("🔍 DEBUGGING CAMPAIGN VALIDATION PIPELINE")
    print("=" * 60)
    
    # Step 1: Check database connection and schema
    print("\n1. DATABASE CONNECTION AND SCHEMA")
    print("-" * 40)
    
    if not os.path.exists('gym_bot.db'):
        print("❌ gym_bot.db not found!")
        return
    
    conn = sqlite3.connect('gym_bot.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check members table structure
    cursor.execute("PRAGMA table_info(members)")
    columns = cursor.fetchall()
    print(f"✅ Members table has {len(columns)} columns:")
    for col in columns:
        print(f"   - {col['name']} ({col['type']})")
    
    # Step 2: Test the exact category mapping from messaging.py
    print("\n2. CATEGORY MAPPING TEST")
    print("-" * 40)
    
    # This is the exact mapping from messaging.py
    category_mapping = {
        'past-due-6-30': 'Past Due 6-30 days',
        'past-due-30-plus': 'Past Due more than 30 days',
        'active-members': 'Active',
        'prospects': 'Prospect',
        'all-members': None  # No filter for all members
    }
    
    test_category = 'past-due-6-30'
    mapped_status = category_mapping.get(test_category)
    print(f"Category '{test_category}' maps to: '{mapped_status}'")
    
    # Step 3: Test database query with exact mapping
    print("\n3. DATABASE QUERY WITH MAPPING")
    print("-" * 40)
    
    if mapped_status:
        query = """
            SELECT 
                prospect_id,
                full_name,
                email,
                mobile_phone,
                status_message
            FROM members 
            WHERE status_message LIKE ?
        """
        cursor.execute(query, (f'%{mapped_status}%',))
    else:
        query = "SELECT prospect_id, full_name, email, mobile_phone, status_message FROM members"
        cursor.execute(query)
    
    members = cursor.fetchall()
    print(f"Query: {query}")
    print(f"Parameter: '%{mapped_status}%'" if mapped_status else "No parameter")
    print(f"Found {len(members)} members")
    
    # Step 4: Analyze contact validation
    print("\n4. CONTACT VALIDATION ANALYSIS")
    print("-" * 40)
    
    valid_email_count = 0
    valid_phone_count = 0
    valid_both_count = 0
    
    for member in members:
        has_email = bool(member['email'] and '@' in member['email'])
        has_phone = bool(member['mobile_phone'] and len(str(member['mobile_phone']).replace('+', '').replace('-', '').replace(' ', '')) >= 10)
        
        if has_email:
            valid_email_count += 1
        if has_phone:
            valid_phone_count += 1
        if has_email and has_phone:
            valid_both_count += 1
        
        # Show first 3 members for debugging
        if len([m for m in members if members.index(m) < 3]) >= members.index(member):
            print(f"  Member: {member['full_name']}")
            print(f"    Email: {'✅' if has_email else '❌'} {member['email']}")
            print(f"    Phone: {'✅' if has_phone else '❌'} {member['mobile_phone']}")
            print(f"    Status: {member['status_message']}")
            print()
    
    print(f"Contact validation summary:")
    print(f"  Valid emails: {valid_email_count}/{len(members)}")
    print(f"  Valid phones: {valid_phone_count}/{len(members)}")
    print(f"  Valid both: {valid_both_count}/{len(members)}")
    
    # Step 5: Simulate exact campaign validation logic
    print("\n5. CAMPAIGN VALIDATION SIMULATION")
    print("-" * 40)
    
    # Test both email and SMS campaign types
    for campaign_type in ['email', 'sms']:
        print(f"\n{campaign_type.upper()} Campaign Validation:")
        
        valid_members = []
        for member in members:
            is_valid = False
            
            if campaign_type == 'email':
                is_valid = bool(member['email'] and '@' in member['email'])
            elif campaign_type == 'sms':
                phone = str(member['mobile_phone']) if member['mobile_phone'] else ''
                clean_phone = phone.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
                is_valid = len(clean_phone) >= 10 and clean_phone.isdigit()
            
            if is_valid:
                valid_members.append(member)
        
        print(f"  Valid members for {campaign_type}: {len(valid_members)}")
        
        if len(valid_members) == 0:
            print(f"  ❌ NO VALID MEMBERS - This would cause the 400 error!")
        else:
            print(f"  ✅ {len(valid_members)} members would be valid for {campaign_type} campaigns")
    
    # Step 6: Check for any filtering issues
    print("\n6. POTENTIAL FILTERING ISSUES")
    print("-" * 40)
    
    # Check if there are any null or empty status messages
    cursor.execute("SELECT COUNT(*) as count FROM members WHERE status_message IS NULL OR status_message = ''")
    null_status = cursor.fetchone()['count']
    print(f"Members with null/empty status_message: {null_status}")
    
    # Check all unique status messages
    cursor.execute("SELECT DISTINCT status_message, COUNT(*) as count FROM members GROUP BY status_message ORDER BY count DESC")
    status_messages = cursor.fetchall()
    print(f"\nAll status messages in database:")
    for status in status_messages:
        print(f"  '{status['status_message']}': {status['count']} members")
    
    # Step 7: Test exact messaging.py query logic
    print("\n7. EXACT MESSAGING.PY QUERY SIMULATION")
    print("-" * 40)
    
    # This simulates the exact query from messaging.py get_members_by_category
    try:
        from src.database.database_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        
        # Test the exact method that's failing
        members_by_category = db_manager.get_members_by_category('past-due-6-30')
        print(f"DatabaseManager.get_members_by_category('past-due-6-30'): {len(members_by_category)} members")
        
        if members_by_category:
            print("✅ DatabaseManager method returns members")
        else:
            print("❌ DatabaseManager method returns no members - THIS IS THE ISSUE!")
            
    except Exception as e:
        print(f"❌ Error testing DatabaseManager: {e}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("🔍 DEBUG COMPLETE - Check output above for validation issues")

if __name__ == "__main__":
    debug_campaign_validation()