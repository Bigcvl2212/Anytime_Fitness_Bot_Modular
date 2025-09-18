#!/usr/bin/env python3
"""
Debug the exact query that messaging.py uses
"""

import sqlite3
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the database manager
try:
    from services.database_manager import DatabaseManager
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Test the exact query from messaging.py
    category_to_use = 'Past Due 6-30 days'
    max_recipients = 100
    
    print(f"Testing query with category: '{category_to_use}'")
    print(f"Using LIKE pattern: '%{category_to_use}%'")
    
    category_members = db_manager.execute_query('''
        SELECT id, prospect_id, email, mobile_phone, full_name, status_message
        FROM members 
        WHERE status_message LIKE ?
        ORDER BY id
        LIMIT ?
    ''', (f'%{category_to_use}%', max_recipients))
    
    print(f"\nQuery returned {len(category_members)} members")
    
    # Validate each member like the messaging route does
    validated_members = []
    message_type = 'email'  # Test email validation
    
    for i, member in enumerate(category_members[:3]):  # Just show first 3
        print(f"\nMember {i+1}:")
        print(f"  Raw data: {dict(member)}")
        
        member_dict = {
            'member_id': member['prospect_id'] or str(member['id']),
            'prospect_id': member['prospect_id'],
            'email': member['email'],
            'mobile_phone': member['mobile_phone'],
            'full_name': member['full_name'],
            'status_message': member['status_message']
        }
        
        print(f"  Processed dict: {member_dict}")
        
        # Test email validation
        email = member_dict.get('email', '').strip()
        if not email or '@' not in email:
            print(f"  ❌ FAILED email validation: email='{email}'")
        else:
            print(f"  ✅ PASSED email validation: email='{email}'")
            validated_members.append(member_dict)
    
    print(f"\n📊 Total validated members: {len(validated_members)}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()