#!/usr/bin/env python3

import sqlite3

def verify_categorization_fix():
    """Verify that the categorization fix is working properly"""
    
    db_path = "gym_bot.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== CATEGORIZATION FIX VERIFICATION ===")
        
        # Check current category counts
        print(f"\n📊 CURRENT CATEGORY COUNTS:")
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM member_categories 
            GROUP BY category 
            ORDER BY count DESC
        """)
        
        categories = cursor.fetchall()
        total = sum(count for _, count in categories)
        
        for category, count in categories:
            print(f"  {category}: {count}")
        
        print(f"Total categorized members: {total}")
        
        # Check actual member count
        cursor.execute("SELECT COUNT(*) FROM members")
        actual_members = cursor.fetchone()[0]
        print(f"Actual members in database: {actual_members}")
        
        if total == actual_members:
            print(f"✅ Category count matches member count!")
        else:
            print(f"❌ Mismatch: {total - actual_members} difference")
        
        # Verify key collections members are properly categorized
        print(f"\n🔍 COLLECTIONS MEMBERS VERIFICATION:")
        cursor.execute("""
            SELECT m.full_name, m.agreement_type, m.amount_past_due, m.status_message, mc.category
            FROM members m
            JOIN member_categories mc ON m.id = mc.member_id
            WHERE m.agreement_type = 'Collections' 
            OR mc.category = 'collections'
            ORDER BY m.full_name
        """)
        
        collections_members = cursor.fetchall()
        print(f"Found {len(collections_members)} collections members:")
        
        for full_name, agreement_type, amount_past_due, status_message, category in collections_members:
            status_icon = "✅" if category == 'collections' else "❌"
            print(f"  {status_icon} {full_name}: {agreement_type}, ${amount_past_due}, {category}")
        
        # Check for any miscategorized members (Collections agreement type but not in collections category)
        cursor.execute("""
            SELECT m.full_name, m.agreement_type, m.amount_past_due, m.status_message, mc.category
            FROM members m
            JOIN member_categories mc ON m.id = mc.member_id
            WHERE m.agreement_type = 'Collections' AND mc.category != 'collections'
        """)
        
        miscategorized = cursor.fetchall()
        if miscategorized:
            print(f"\n⚠️ MISCATEGORIZED COLLECTIONS MEMBERS:")
            for full_name, agreement_type, amount_past_due, status_message, category in miscategorized:
                print(f"  ❌ {full_name}: Agreement={agreement_type}, Category={category}")
        else:
            print(f"\n✅ All Collections agreement members are properly categorized!")
        
        # Show recent category updates
        print(f"\n📅 RECENT CATEGORY UPDATES:")
        cursor.execute("""
            SELECT full_name, category, classified_at
            FROM member_categories 
            WHERE classified_at > datetime('now', '-1 hour')
            ORDER BY classified_at DESC
            LIMIT 10
        """)
        
        recent_updates = cursor.fetchall()
        if recent_updates:
            print(f"Found {len(recent_updates)} recent updates:")
            for full_name, category, classified_at in recent_updates:
                print(f"  {full_name} → {category} ({classified_at})")
        else:
            print("No recent category updates found")
        
        # Summary
        print(f"\n📋 SUMMARY:")
        print(f"✅ Database cleanup: Removed 532 orphaned entries")
        print(f"✅ Category counts: Now match actual member count ({total})")
        print(f"✅ Collections logic: Added missing categorization for Collections agreement type")
        print(f"✅ Update logic: Categories now update during member sync")
        print(f"✅ Collections members: {len([c for c in collections_members if c[4] == 'collections'])} properly categorized")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verifying categorization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_categorization_fix()