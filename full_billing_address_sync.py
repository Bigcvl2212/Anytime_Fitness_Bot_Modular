"""
Trigger full member sync WITH billing/agreement data AND addresses
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.multi_club_startup_sync import sync_members_for_club
from src.services.database_manager import DatabaseManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 80)
print("FULL MEMBER SYNC WITH BILLING DATA AND ADDRESSES")
print("=" * 80)

print("\n🔄 Starting member sync with agreement data...")
print("(This will take a few minutes to process all agreements)\n")

# Sync members with all data including agreements
members = sync_members_for_club(club_id='1156', app=None, manager_id=None)

if members:
    print(f"\n✅ Synced {len(members)} members with billing data")
    
    # Save to database
    print("\n💾 Saving to database...")
    db = DatabaseManager()
    success = db.save_members_to_db(members)
    
    if success:
        print(f"✅ Saved {len(members)} members to database!")
        
        # Check past due members
        import sqlite3
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT full_name, address, city, state, zip_code, amount_past_due
            FROM members 
            WHERE status_message LIKE '%Past Due%'
            ORDER BY amount_past_due DESC
            LIMIT 10
        """)
        
        past_due = cursor.fetchall()
        conn.close()
        
        print(f"\n📊 PAST DUE MEMBERS WITH ADDRESSES:")
        print("=" * 80)
        for row in past_due:
            print(f"\n{row[0]}")
            print(f"  Address: {row[1] or 'NO ADDRESS'}")
            print(f"  City/State/Zip: {row[2] or 'NO CITY'}, {row[3] or 'NO STATE'} {row[4] or 'NO ZIP'}")
            print(f"  Past Due: ${row[5]:.2f}")
    else:
        print("❌ Failed to save to database")
else:
    print("❌ No members returned from sync")
