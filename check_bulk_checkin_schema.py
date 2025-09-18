#!/usr/bin/env python3
"""
Check gym_bot.db schema and fix bulk check-in issues
"""

import sqlite3

def check_schema_and_data():
    """Check the actual schema and data in gym_bot.db"""
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    print("🗄️ Checking members table schema:")
    cursor.execute("PRAGMA table_info(members)")
    columns = cursor.fetchall()
    
    column_names = []
    for col in columns:
        column_names.append(col[1])
        print(f"   {col[1]} ({col[2]})" + (" NOT NULL" if col[3] else ""))
    
    print(f"\n📋 Available columns: {column_names}")
    
    # Check for problematic columns that don't exist
    missing_columns = []
    for required_col in ['member_type', 'agreement_type']:
        if required_col not in column_names:
            missing_columns.append(required_col)
    
    if missing_columns:
        print(f"❌ Missing columns that cause null errors: {missing_columns}")
    
    # Count all members by status
    print(f"\n📊 Member counts by status:")
    cursor.execute("SELECT status, COUNT(*) FROM members GROUP BY status ORDER BY status")
    status_counts = cursor.fetchall()
    for status, count in status_counts:
        print(f"   Status {status}: {count} members")
    
    # Count members by status_message
    print(f"\n📊 Member counts by status_message (top 10):")
    cursor.execute("""
        SELECT status_message, COUNT(*) as count 
        FROM members 
        WHERE status_message IS NOT NULL AND status_message != ''
        GROUP BY status_message 
        ORDER BY count DESC 
        LIMIT 10
    """)
    status_msg_counts = cursor.fetchall()
    for status_msg, count in status_msg_counts:
        print(f"   '{status_msg}': {count} members")
    
    # Check for PPV indicators in existing data
    print(f"\n🔍 Checking for PPV indicators:")
    if 'user_type' in column_names:
        cursor.execute("SELECT user_type, COUNT(*) FROM members GROUP BY user_type ORDER BY user_type")
        user_types = cursor.fetchall()
        for user_type, count in user_types:
            print(f"   user_type {user_type}: {count} members")
    
    # Sample of members with different patterns
    print(f"\n📋 Sample members for PPV detection:")
    cursor.execute("""
        SELECT prospect_id, full_name, status_message, user_type, status 
        FROM members 
        WHERE status_message IS NOT NULL 
        ORDER BY prospect_id 
        LIMIT 10
    """)
    samples = cursor.fetchall()
    for sample in samples:
        print(f"   {sample[1]} (ID: {sample[0]}) - Status: '{sample[2]}' - UserType: {sample[3]} - Active: {sample[4]}")
    
    conn.close()

if __name__ == "__main__":
    check_schema_and_data()