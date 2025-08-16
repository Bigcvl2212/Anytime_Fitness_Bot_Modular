#!/usr/bin/env python3
"""Check database contents"""

import sqlite3

def check_database():
    """Check what's in the database"""
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print("Tables:", tables)
    
    # Check members table
    if 'members' in tables:
        cursor.execute("SELECT COUNT(*) FROM members")
        count = cursor.fetchone()[0]
        print(f"Members count: {count}")
        
        if count > 0:
            cursor.execute("SELECT first_name, last_name, id FROM members LIMIT 5")
            print("Sample members:")
            for row in cursor.fetchall():
                print(f"  {row[0]} {row[1]} (ID: {row[2]})")
    
    # Check training_clients table
    if 'training_clients' in tables:
        cursor.execute("SELECT COUNT(*) FROM training_clients")
        count = cursor.fetchone()[0]
        print(f"Training clients count: {count}")
        
        if count > 0:
            cursor.execute("SELECT member_name, clubos_member_id FROM training_clients LIMIT 5")
            print("Sample training clients:")
            for row in cursor.fetchall():
                print(f"  {row[0]} (ClubOS ID: {row[1]})")
    
    conn.close()

if __name__ == "__main__":
    check_database()




