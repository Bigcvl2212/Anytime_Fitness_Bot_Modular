#!/usr/bin/env python3
"""
Direct sync bypassing the multi-club manager issue
"""

import os
import sys
sys.path.append('src')

# Set up environment
from src.config.environment_setup import load_environment_variables, validate_environment_setup
load_environment_variables()

import logging
logging.basicConfig(level=logging.INFO)

from src.services.database_manager import DatabaseManager
from src.services.multi_club_startup_sync import sync_members_for_club, sync_prospects_for_club, sync_training_clients_for_club

print("🔄 Starting direct sync (bypassing multi-club manager)...")

# Initialize database manager
db_manager = DatabaseManager()
print("✅ Database manager initialized")

try:
    # Directly sync each data type for club 1156
    print("📊 Syncing members for club 1156...")
    members = sync_members_for_club(club_id='1156')
    print(f"✅ Retrieved {len(members)} members")

    print("📊 Syncing prospects for club 1156...")
    prospects = sync_prospects_for_club(club_id='1156')
    print(f"✅ Retrieved {len(prospects)} prospects")

    print("📊 Syncing training clients for club 1156...")
    training_clients = sync_training_clients_for_club(club_id='1156')
    print(f"✅ Retrieved {len(training_clients)} training clients")

    # Save to database
    if members:
        print(f"💾 Saving {len(members)} members to database...")
        success = db_manager.save_members_to_db(members)
        if success:
            print(f"✅ Successfully saved {len(members)} members with categorization")
        else:
            print("❌ Failed to save members")

    if prospects:
        print(f"💾 Saving {len(prospects)} prospects to database...")
        success = db_manager.save_prospects_to_db(prospects)
        if success:
            print(f"✅ Successfully saved {len(prospects)} prospects")
        else:
            print("❌ Failed to save prospects")

    if training_clients:
        print(f"💾 Saving {len(training_clients)} training clients to database...")
        success = db_manager.save_training_clients_to_db(training_clients)
        if success:
            print(f"✅ Successfully saved {len(training_clients)} training clients")
        else:
            print("❌ Failed to save training clients")

    # Verify database
    print("\n📊 Checking database...")
    import psycopg2.extras
    conn = db_manager.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cur.execute('SELECT COUNT(*) as count FROM members')
    member_count = cur.fetchone()['count']
    print(f"📊 Members in database: {member_count}")
    
    cur.execute('SELECT COUNT(*) as count FROM member_categories')
    category_count = cur.fetchone()['count']
    print(f"📊 Member categories in database: {category_count}")
    
    # Check category breakdown
    cur.execute('SELECT category, COUNT(*) as count FROM member_categories GROUP BY category ORDER BY count DESC')
    categories = cur.fetchall()
    print("📊 Category breakdown:")
    for cat in categories:
        print(f"  {cat['category']}: {cat['count']}")
    
    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("✅ Direct sync complete!")