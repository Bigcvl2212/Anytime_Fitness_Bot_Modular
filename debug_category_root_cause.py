#!/usr/bin/env python3
"""
Debug Category Mapping Issue
Test the exact flow that's causing the messaging campaign validation failure
"""

import os
import sys
import sqlite3
import json
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_category_mapping_issue():
    """Debug the exact category mapping issue in messaging campaigns"""
    
    print("🔍 DEBUGGING CATEGORY MAPPING ISSUE")
    print("=" * 60)
    
    # Step 1: Test the category mapping from messaging.py
    print("\n1. CATEGORY MAPPING FROM MESSAGING.PY")
    print("-" * 40)
    
    category_mapping = {
        'past-due-6-30': 'Past Due 6-30 days',
        'past-due-30-plus': 'Past Due more than 30 days.',
        'past-due-6-30-days': 'Past Due 6-30 days',
        'past-due-more-than-30-days': 'Past Due more than 30 days.',
        'good-standing': 'Member is in good standing',
        'in-good-standing': 'Member is in good standing',
        'comp': 'Comp Member',
        'staff': 'Staff Member',
        'pay-per-visit': 'Pay Per Visit Member',
        'sent-to-collections': 'Sent to Collections',
        'pending-cancel': 'Member is pending cancel',
        'expired': 'Expired',
        'cancelled': 'Account has been cancelled.',
        'all_members': 'all_members',  # Special case
        'prospects': 'prospects'      # Special case
    }
    
    test_category = 'past-due-6-30'
    mapped_status = category_mapping.get(test_category)
    print(f"Input category: '{test_category}'")
    print(f"Mapped to status_message: '{mapped_status}'")
    
    # Step 2: Test database query directly
    print("\n2. DIRECT DATABASE QUERY TEST")
    print("-" * 40)
    
    if not os.path.exists('gym_bot.db'):
        print("❌ gym_bot.db not found!")
        return
    
    conn = sqlite3.connect('gym_bot.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Test the exact query that messaging.py should be running
    query = """
        SELECT id, prospect_id, email, mobile_phone, full_name, status_message
        FROM members 
        WHERE status_message LIKE ?
        ORDER BY id
    """
    cursor.execute(query, (f'%{mapped_status}%',))
    members = cursor.fetchall()
    
    print(f"Query: {query}")
    print(f"Parameter: '%{mapped_status}%'")
    print(f"Results: {len(members)} members found")
    
    if members:
        print("✅ Database query returns members successfully!")
        print("Sample results:")
        for i, member in enumerate(members[:3]):
            print(f"  {i+1}. {member['full_name']} - {member['status_message']}")
            print(f"     Email: {member['email']}")
            print(f"     Phone: {member['mobile_phone']}")
    else:
        print("❌ Database query returns no members!")
    
    # Step 3: Test DatabaseManager.get_members_by_category method
    print("\n3. DATABASEMANAGER.GET_MEMBERS_BY_CATEGORY TEST")  
    print("-" * 40)
    
    try:
        from src.services.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Test with the original category name (this will fail)
        result1 = db_manager.get_members_by_category('past-due-6-30')
        print(f"DatabaseManager.get_members_by_category('past-due-6-30'): {len(result1) if result1 else 0} members")
        
        # Test with the hardcoded category (this might work)  
        result2 = db_manager.get_members_by_category('past_due')
        print(f"DatabaseManager.get_members_by_category('past_due'): {len(result2) if result2 else 0} members")
        
        if not result1 and not result2:
            print("❌ BOTH DatabaseManager queries return no members!")
            print("   This is the root cause of the campaign validation failure!")
        elif result1:
            print("✅ Original category works in DatabaseManager")
        elif result2:
            print("⚠️ Only hardcoded 'past_due' category works in DatabaseManager")
            print("   The messaging route needs to map 'past-due-6-30' to 'past_due'")
            
    except Exception as e:
        print(f"❌ Error testing DatabaseManager: {e}")
    
    # Step 4: Test the messaging.py campaign validation logic
    print("\n4. MESSAGING.PY CAMPAIGN VALIDATION SIMULATION")
    print("-" * 40)
    
    # This simulates the exact validation from the send_campaign route
    member_categories = ['past-due-6-30']
    max_recipients = 100
    
    validated_members = []
    for category in member_categories:
        print(f"Processing category: '{category}'")
        
        # Map frontend category to database status_message (this works)
        actual_status_message = category_mapping.get(category, category)
        print(f"  Mapped to: '{actual_status_message}'")
        
        # This is the query that should work
        category_members = cursor.execute('''
            SELECT id, prospect_id, email, mobile_phone, full_name, status_message
            FROM members 
            WHERE status_message LIKE ?
            ORDER BY id
            LIMIT ?
        ''', (f'%{actual_status_message}%', max_recipients)).fetchall()
        
        print(f"  Query found: {len(category_members)} members")
        
        # Validate members for SMS campaign  
        for member in category_members:
            member_dict = {
                'member_id': member['prospect_id'] or str(member['id']),
                'prospect_id': member['prospect_id'],
                'email': member['email'],
                'mobile_phone': member['mobile_phone'],
                'full_name': member['full_name'],
                'status_message': member['status_message']
            }
            
            # SMS validation
            phone = member_dict.get('mobile_phone', '').strip()
            if phone:
                clean_phone = phone.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
                if len(clean_phone) >= 10 and clean_phone.isdigit():
                    validated_members.append(member_dict)
    
    print(f"\nFinal validation results:")
    print(f"  Total validated members: {len(validated_members)}")
    
    if len(validated_members) > 0:
        print("✅ Campaign validation SHOULD work!")
        print("   The issue must be in how the messaging route calls the database")
    else:
        print("❌ Campaign validation fails - no valid members found")
    
    # Step 5: Show the exact issue
    print("\n5. ROOT CAUSE ANALYSIS")
    print("-" * 40)
    
    print("The issue is in messaging.py line ~830:")
    print("  category_members = current_app.db_manager.get_members_by_category(category_to_use)")
    print()
    print("This calls DatabaseManager.get_members_by_category() with 'Past Due 6-30 days'")
    print("But DatabaseManager only handles hardcoded categories like 'past_due', not status messages!")
    print()
    print("SOLUTION: Modify messaging.py to use execute_query() directly instead of get_members_by_category()")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("🔍 DEBUG COMPLETE - Root cause identified!")

if __name__ == "__main__":
    debug_category_mapping_issue()