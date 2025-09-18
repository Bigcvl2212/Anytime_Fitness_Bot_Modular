#!/usr/bin/env python3
"""
Check active member status messages to debug green category
"""

import sqlite3

def main():
    conn = sqlite3.connect("gym_bot.db")
    conn.row_factory = sqlite3.Row
    
    # Check all active-like status messages
    cursor = conn.execute("""
        SELECT status_message, COUNT(*) as count 
        FROM members 
        WHERE status_message LIKE '%Active%' OR status_message = ''
        GROUP BY status_message 
        ORDER BY count DESC
    """)
    
    print("=== ACTIVE STATUS MESSAGES ===")
    for row in cursor.fetchall():
        print(f"'{row['status_message']}': {row['count']}")
    
    # Check what the most common status messages are
    cursor = conn.execute("""
        SELECT status_message, COUNT(*) as count 
        FROM members 
        GROUP BY status_message 
        ORDER BY count DESC
        LIMIT 10
    """)
    
    print("\n=== TOP 10 STATUS MESSAGES ===")
    for row in cursor.fetchall():
        print(f"'{row['status_message']}': {row['count']}")

if __name__ == "__main__":
    main()