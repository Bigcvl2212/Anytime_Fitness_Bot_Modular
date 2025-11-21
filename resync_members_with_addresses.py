"""
Quick script to trigger member refresh with address data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.multi_club_startup_sync import sync_members_for_club
from src.services.database_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 80)
print("TRIGGERING MEMBER RESYNC WITH ADDRESS DATA")
print("=" * 80)

# Sync members (will get addresses from ClubHub API)
members = sync_members_for_club()

if members:
    print(f"\n✅ Got {len(members)} members from ClubHub")
    
    # Check how many have addresses
    with_address = len([m for m in members if m.get('address')])
    with_zip = len([m for m in members if m.get('zip_code')])
    
    print(f"📍 Members with street address: {with_address} ({with_address/len(members)*100:.1f}%)")
    print(f"📍 Members with zip code: {with_zip} ({with_zip/len(members)*100:.1f}%)")
    
    # Save to database
    print(f"\n💾 Saving members to database...")
    db = DatabaseManager()
    success = db.save_members_to_db(members)
    
    if success:
        print(f"✅ Successfully saved {len(members)} members to database with address data!")
        
        # Verify database has addresses now
        import sqlite3
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM members WHERE address IS NOT NULL AND address != ''")
        db_with_address = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM members WHERE zip_code IS NOT NULL AND zip_code != ''")
        db_with_zip = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM members")
        total_members = cursor.fetchone()[0]
        
        print(f"\n📊 DATABASE VERIFICATION:")
        print(f"   Total members in DB: {total_members}")
        print(f"   With street address: {db_with_address} ({db_with_address/total_members*100:.1f}%)")
        print(f"   With zip code: {db_with_zip} ({db_with_zip/total_members*100:.1f}%)")
        
        # Show sample of past due members with addresses
        print(f"\n📍 SAMPLE PAST DUE MEMBERS WITH ADDRESSES:")
        cursor.execute("""
            SELECT full_name, address, city, state, zip_code, amount_past_due
            FROM members
            WHERE status_message LIKE '%Past Due%'
            AND address IS NOT NULL
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            print(f"   {row[0]}: {row[1]}, {row[2]}, {row[3]} {row[4]} - ${row[5]:.2f}")
        
        conn.close()
    else:
        print(f"❌ Failed to save members to database")
else:
    print(f"❌ No members returned from sync")
