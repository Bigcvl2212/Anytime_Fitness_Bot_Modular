#!/usr/bin/env python3
"""
Check member category data to debug tab display issues
"""

import os
import sys
from src.services.database_manager import DatabaseManager

def check_member_categories():
    """Check what member category data exists in the database"""
    print("🔍 Checking member category data...")
    
    # Initialize database manager with SQLite override
    project_root = os.getcwd()
    db_path = os.path.join(project_root, 'gym_bot.db')
    
    # Override environment to force SQLite
    os.environ['DB_TYPE'] = 'sqlite'
    db = DatabaseManager(db_path=db_path)
    
    print("\n=== TOTAL MEMBERS ===")
    result = db.execute_query('SELECT COUNT(*) as count FROM members')
    total_members = result[0]['count'] if result else 0
    print(f"Total members in database: {total_members}")
    
    print("\n=== STATUS MESSAGE ANALYSIS ===")
    result = db.execute_query('SELECT status_message, COUNT(*) as count FROM members GROUP BY status_message ORDER BY count DESC LIMIT 20')
    if result:
        for row in result:
            print(f'{row["count"]:3d} - "{row["status_message"]}"')
    else:
        print("No status message results")
    
    print("\n=== AGREEMENT ID ANALYSIS ===")
    result = db.execute_query('SELECT CASE WHEN agreement_id IS NULL THEN "NULL" ELSE "HAS_AGREEMENT" END as agreement_status, COUNT(*) as count FROM members GROUP BY agreement_status ORDER BY count DESC')
    if result:
        for row in result:
            print(f'{row["count"]:3d} - "{row["agreement_status"]}"')
    else:
        print("No agreement ID results")
    
    print("\n=== SPECIFIC CATEGORY TESTS ===")
    
    # Test yellow members
    result = db.execute_query('''
        SELECT COUNT(*) as count FROM members
        WHERE status_message IN (
            'Invalid Billing Information.',
            'Invalid/Bad Address information.',
            'Member is pending cancel',
            'Member will expire within 30 days.'
        )
    ''')
    yellow_count = result[0]['count'] if result else 0
    print(f"Yellow members (billing issues): {yellow_count}")
    
    # Test collections members 
    result = db.execute_query('''
        SELECT COUNT(*) as count FROM members
        WHERE agreement_id IS NULL
        AND status_message NOT IN ('Member is in good standing', 'In good standing')
    ''')
    collections_count = result[0]['count'] if result else 0
    print(f"Collections members: {collections_count}")
    
    # Test inactive members
    result = db.execute_query('''
        SELECT COUNT(*) as count FROM members
        WHERE (
            status IN ('Inactive','inactive','Suspended','suspended','Cancelled','cancelled')
            OR status_message IN ('Expired', 'Account has been cancelled.')
            OR status_message LIKE '%suspend%'
            OR status_message IS NULL
            OR (
                status_message IN ('Staff Member', 'Staff member', '') 
                AND prospect_id NOT IN ('191003722', '189425730', '191210406', '191015549', '191201279')
            )
        )
        AND agreement_id IS NOT NULL
        AND status_message != 'Sent to Collections'
    ''')
    inactive_count = result[0]['count'] if result else 0
    print(f"Inactive members: {inactive_count}")
    
    print("\n=== ALTERNATE YELLOW PATTERNS ===")
    # Check for different yellow patterns
    patterns = [
        "billing",
        "address", 
        "pending",
        "expire",
        "invalid",
        "bad"
    ]
    
    for pattern in patterns:
        result = db.execute_query(f"SELECT COUNT(*) as count FROM members WHERE LOWER(status_message) LIKE '%{pattern}%'")
        count = result[0]['count'] if result else 0
        if count > 0:
            print(f"  '{pattern}' pattern: {count}")
    
    print("\n=== ALTERNATE COLLECTIONS PATTERNS ===")
    # Check for different collections patterns
    result = db.execute_query("SELECT COUNT(*) as count FROM members WHERE LOWER(status_message) LIKE '%collection%'")
    count = result[0]['count'] if result else 0
    print(f"Status message contains 'collection': {count}")
    
    result = db.execute_query("SELECT COUNT(*) as count FROM members WHERE agreement_id IS NULL")
    count = result[0]['count'] if result else 0
    print(f"Members with NULL agreement_id: {count}")
    
    print("\n=== ALTERNATE INACTIVE PATTERNS ===")
    # Check for different inactive patterns
    patterns = [
        "cancel",
        "suspend",
        "inactive",
        "expired"
    ]
    
    for pattern in patterns:
        result = db.execute_query(f"SELECT COUNT(*) as count FROM members WHERE LOWER(status_message) LIKE '%{pattern}%'")
        count = result[0]['count'] if result else 0
        if count > 0:
            print(f"  '{pattern}' pattern: {count}")
    
    print("\n=== SAMPLE MEMBER DATA ===")
    # Get a few sample members to see actual data structure
    result = db.execute_query("SELECT id, guid, prospect_id, first_name, last_name, status_message, agreement_id, agreement_status LIMIT 5")
    if result:
        for row in result:
            print(f"ID: {row['id']}, GUID: {row['guid']}, Prospect: {row['prospect_id']}")
            print(f"  Name: {row['first_name']} {row['last_name']}")
            print(f"  Status Message: '{row['status_message']}'")
            print(f"  Agreement ID: {row['agreement_id']}")
            print(f"  Agreement Status: '{row['agreement_status']}'")
            print()

if __name__ == "__main__":
    check_member_categories()