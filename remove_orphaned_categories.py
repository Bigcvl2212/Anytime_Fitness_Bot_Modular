#!/usr/bin/env python3

import sqlite3

def remove_orphaned_categories():
    """Remove all orphaned category entries that don't have matching members"""
    
    db_path = "gym_bot.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== REMOVING ORPHANED CATEGORY ENTRIES ===")
        
        # First, get count of orphaned entries
        cursor.execute("""
            SELECT COUNT(*)
            FROM member_categories mc
            LEFT JOIN members m ON mc.member_id = m.id
            WHERE m.id IS NULL
        """)
        orphaned_count = cursor.fetchone()[0]
        print(f"Found {orphaned_count} orphaned category entries to remove")
        
        if orphaned_count == 0:
            print("✅ No orphaned entries found - database is clean!")
            return
        
        # Show sample of what will be deleted
        print(f"\nSample of entries to be deleted:")
        cursor.execute("""
            SELECT mc.member_id, mc.category, mc.created_at
            FROM member_categories mc
            LEFT JOIN members m ON mc.member_id = m.id
            WHERE m.id IS NULL
            LIMIT 10
        """)
        
        samples = cursor.fetchall()
        for member_id, category, created_at in samples:
            print(f"   Member ID {member_id} -> {category} ({created_at})")
        
        if len(samples) == 10 and orphaned_count > 10:
            print(f"   ... and {orphaned_count - 10} more")
        
        # Get counts before deletion
        cursor.execute("SELECT COUNT(*) FROM member_categories")
        total_before = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT member_id) FROM member_categories")
        unique_before = cursor.fetchone()[0]
        
        print(f"\nBEFORE CLEANUP:")
        print(f"   Total category entries: {total_before}")
        print(f"   Unique members with categories: {unique_before}")
        
        # Delete orphaned entries
        cursor.execute("""
            DELETE FROM member_categories 
            WHERE member_id NOT IN (
                SELECT id FROM members
            )
        """)
        
        deleted_count = cursor.rowcount
        print(f"\n🗑️ DELETED {deleted_count} orphaned category entries")
        
        # Get counts after deletion
        cursor.execute("SELECT COUNT(*) FROM member_categories")
        total_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT member_id) FROM member_categories")
        unique_after = cursor.fetchone()[0]
        
        # Get actual member count for comparison
        cursor.execute("SELECT COUNT(*) FROM members")
        actual_members = cursor.fetchone()[0]
        
        print(f"\nAFTER CLEANUP:")
        print(f"   Total category entries: {total_after}")
        print(f"   Unique members with categories: {unique_after}")
        print(f"   Actual members in database: {actual_members}")
        
        if unique_after == actual_members:
            print(f"✅ SUCCESS: Category count now matches member count!")
        else:
            print(f"⚠️ Still {abs(unique_after - actual_members)} difference between category and member count")
        
        # Show final category breakdown
        print(f"\n=== FINAL CATEGORY BREAKDOWN ===")
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM member_categories 
            GROUP BY category 
            ORDER BY count DESC
        """)
        
        categories = cursor.fetchall()
        total_final = sum(count for _, count in categories)
        
        for category, count in categories:
            print(f"  {category}: {count}")
        
        print(f"\nTotal: {total_final}")
        
        # Commit the changes
        conn.commit()
        print(f"\n✅ Changes committed to database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error removing orphaned categories: {e}")
        if 'conn' in locals():
            conn.rollback()

if __name__ == "__main__":
    remove_orphaned_categories()