#!/usr/bin/env python3
"""
Check actual database schema and member data
"""

import os
from src.services.database_manager import DatabaseManager

def main():
    # Set local development
    os.environ['LOCAL_DEVELOPMENT'] = 'true'
    
    db = DatabaseManager()
    
    # Check if members table exists and what columns it has
    try:
        schema = db.execute_query("PRAGMA table_info(members)")
        print("Members table schema:")
        for col in schema:
            print(f"  {col['name']} ({col['type']})")
        print()
    except Exception as e:
        print(f"Error getting schema: {e}")
    
    # Count total members
    try:
        total = db.execute_query('SELECT COUNT(*) as count FROM members')
        print(f'Total members in database: {total[0]["count"] if total else "No data"}')
    except Exception as e:
        print(f"Error counting members: {e}")
    
    # Sample members
    try:
        sample = db.execute_query('SELECT * FROM members LIMIT 5')
        print(f'\nSample members ({len(sample)} found):')
        for member in sample:
            print(f'  {member.get("full_name", "Unknown")} (ID: {member.get("prospect_id", "N/A")}) - Status: {member.get("status_message", "N/A")}')
    except Exception as e:
        print(f"Error getting sample members: {e}")

if __name__ == "__main__":
    main()