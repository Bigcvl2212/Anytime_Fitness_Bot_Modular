#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Database Schema for Sync - November 3, 2025
Add missing columns: member_type, club_name
"""

import sqlite3
import sys

def fix_schema():
    """Add missing columns to members and prospects tables"""
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()

        print("Fixing database schema for sync...")

        # Check if member_type exists in members table
        cursor.execute("PRAGMA table_info(members)")
        members_cols = [row[1] for row in cursor.fetchall()]

        if 'member_type' not in members_cols:
            print("Adding member_type column to members table...")
            cursor.execute("ALTER TABLE members ADD COLUMN member_type TEXT")
            print("Added member_type column")
        else:
            print("member_type column already exists in members table")

        # Check if club_name exists in prospects table
        cursor.execute("PRAGMA table_info(prospects)")
        prospects_cols = [row[1] for row in cursor.fetchall()]

        if 'club_name' not in prospects_cols:
            print("Adding club_name column to prospects table...")
            cursor.execute("ALTER TABLE prospects ADD COLUMN club_name TEXT")
            print("Added club_name column")
        else:
            print("club_name column already exists in prospects table")

        # Also add club_name to members table if missing
        if 'club_name' not in members_cols:
            print("Adding club_name column to members table...")
            cursor.execute("ALTER TABLE members ADD COLUMN club_name TEXT")
            print("Added club_name column to members table")
        else:
            print("club_name column already exists in members table")

        conn.commit()

        # Verify the changes
        print("\nVerifying schema changes...")
        cursor.execute("PRAGMA table_info(members)")
        members_cols = [row[1] for row in cursor.fetchall()]
        print(f"Members table columns: {len(members_cols)} total")
        print(f"   - member_type: {'YES' if 'member_type' in members_cols else 'NO'}")
        print(f"   - club_name: {'YES' if 'club_name' in members_cols else 'NO'}")

        cursor.execute("PRAGMA table_info(prospects)")
        prospects_cols = [row[1] for row in cursor.fetchall()]
        print(f"Prospects table columns: {len(prospects_cols)} total")
        print(f"   - club_name: {'YES' if 'club_name' in prospects_cols else 'NO'}")

        # Get row counts
        cursor.execute("SELECT COUNT(*) FROM members")
        member_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM prospects")
        prospect_count = cursor.fetchone()[0]

        print(f"\nCurrent data:")
        print(f"   - Members: {member_count}")
        print(f"   - Prospects: {prospect_count}")

        conn.close()

        print("\nSchema fix complete!")
        print("Ready for next sync - columns added successfully")
        return True

    except Exception as e:
        print(f"Error fixing schema: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_schema()
    sys.exit(0 if success else 1)
