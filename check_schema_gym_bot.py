#!/usr/bin/env python3
"""
Check gym_bot.db schema and update bulk check-in query
"""

import sqlite3

def main():
    # Check the schema of gym_bot.db
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    # Get members table schema
    cursor.execute("PRAGMA table_info(members)")
    schema = cursor.fetchall()
    
    print("🗄️ Members table schema in gym_bot.db:")
    for col in schema:
        print(f"   {col[1]} ({col[2]})" + (" NOT NULL" if col[3] else ""))
    
    # Check for the problematic columns
    column_names = [col[1] for col in schema]
    missing_columns = []
    
    for required_col in ['member_type', 'agreement_type']:
        if required_col not in column_names:
            missing_columns.append(required_col)
    
    if missing_columns:
        print(f"\n❌ Missing columns that cause null reference errors: {missing_columns}")
    else:
        print(f"\n✅ All required columns exist")
    
    # Count eligible members with the current query structure
    cursor.execute("""
        SELECT COUNT(*) FROM members 
        WHERE status_message NOT LIKE '%cancelled%' 
        AND status_message NOT LIKE '%expired%' 
        AND status_message NOT LIKE '%inactive%' 
        AND status > 0
    """)
    eligible_count = cursor.fetchone()[0]
    
    print(f"\n📊 Eligible members for bulk check-in: {eligible_count}")
    
    # Sample some of the eligible members
    cursor.execute("""
        SELECT prospect_id, first_name, last_name, full_name, status_message, 
               user_type, status
        FROM members 
        WHERE status_message NOT LIKE '%cancelled%' 
        AND status_message NOT LIKE '%expired%' 
        AND status_message NOT LIKE '%inactive%' 
        AND status > 0
        LIMIT 5
    """)
    
    samples = cursor.fetchall()
    print(f"\n📋 Sample eligible members:")
    for member in samples:
        print(f"   {member[3]} (ID: {member[0]}) - Status: {member[4]}")
    
    conn.close()

if __name__ == "__main__":
    main()