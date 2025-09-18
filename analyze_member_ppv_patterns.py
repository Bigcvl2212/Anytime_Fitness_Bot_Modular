#!/usr/bin/env python3

"""
Analyze Member Database for PPV Status Indicators
===============================================

This script analyzes the members table to find columns that might indicate
green/red/yellow status or PPV membership types.
"""

import sqlite3

def analyze_member_database():
    """Analyze member database for PPV and status indicators"""
    
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    print("=== All tables in database ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    for table in tables:
        print(f"- {table[0]}")
    
    print("\n=== Sample member data to find PPV patterns ===")
    cursor.execute("SELECT * FROM members LIMIT 5")
    sample_rows = cursor.fetchall()
    cursor.execute("PRAGMA table_info(members)")
    columns = cursor.fetchall()
    
    print("Column names:")
    for i, col in enumerate(columns):
        print(f"{i+1:2d}. {col[1]}")
    
    print("\nSample member records:")
    for i, row in enumerate(sample_rows):
        print(f"\n--- Member {i+1} ---")
        for j, col in enumerate(columns):
            col_name = col[1]
            value = row[j]
            if value is not None and str(value).strip():
                print(f"  {col_name}: {value}")
    
    print("\n=== Looking for PPV members by status_message patterns ===")
    cursor.execute("""
        SELECT status_message, COUNT(*) as count, 
               MIN(full_name) as sample_name
        FROM members 
        WHERE status_message LIKE '%visit%' 
           OR status_message LIKE '%PPV%'
           OR status_message LIKE '%per visit%'
           OR status_message LIKE '%day pass%'
           OR status_message LIKE '%guest%'
        GROUP BY status_message 
        ORDER BY count DESC
    """)
    
    ppv_patterns = cursor.fetchall()
    total_ppv_found = 0
    
    if ppv_patterns:
        print("Found potential PPV patterns:")
        for status_msg, count, sample_name in ppv_patterns:
            print(f"  '{status_msg}': {count} members (sample: {sample_name})")
            total_ppv_found += count
    else:
        print("No obvious PPV patterns found in status_message")
    
    print(f"\nTotal potential PPV members found by pattern: {total_ppv_found}")
    
    print("\n=== Checking specific status values ===")
    cursor.execute("""
        SELECT status, status_message, COUNT(*) as count,
               MIN(full_name) as sample_name
        FROM members 
        WHERE status IN ('0', '1', '7', '')
        GROUP BY status, status_message
        ORDER BY status, count DESC
        LIMIT 20
    """)
    
    status_breakdown = cursor.fetchall()
    print("Status breakdown:")
    for status, status_msg, count, sample_name in status_breakdown:
        print(f"  Status '{status}' + '{status_msg}': {count} members (sample: {sample_name})")
    
    print("\n=== Checking for members with high past due amounts (might indicate different membership types) ===")
    cursor.execute("""
        SELECT amount_past_due, status_message, COUNT(*) as count,
               MIN(full_name) as sample_name
        FROM members 
        WHERE amount_past_due > 0
        GROUP BY amount_past_due, status_message
        ORDER BY amount_past_due DESC
        LIMIT 10
    """)
    
    past_due_patterns = cursor.fetchall()
    print("Past due amount patterns:")
    for amount, status_msg, count, sample_name in past_due_patterns:
        print(f"  ${amount} past due + '{status_msg}': {count} members (sample: {sample_name})")
    
    conn.close()

if __name__ == "__main__":
    analyze_member_database()