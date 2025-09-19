#!/usr/bin/env python3

import sqlite3

def analyze_member_discrepancy():
    """Compare actual member count with categorized members to find discrepancy"""
    
    db_path = "gym_bot.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== MEMBER COUNT ANALYSIS ===")
        
        # Get total members in main table
        cursor.execute("SELECT COUNT(*) FROM members")
        total_members = cursor.fetchone()[0]
        print(f"Total members in 'members' table: {total_members}")
        
        # Get unique members in categories table
        cursor.execute("SELECT COUNT(DISTINCT member_id) FROM member_categories")
        categorized_members = cursor.fetchone()[0]
        print(f"Unique members in 'member_categories' table: {categorized_members}")
        
        # Get total category entries (including any duplicates per member)
        cursor.execute("SELECT COUNT(*) FROM member_categories")
        total_category_entries = cursor.fetchone()[0]
        print(f"Total category entries: {total_category_entries}")
        
        print(f"\n❌ DISCREPANCY: {categorized_members - total_members} extra categorized members")
        print(f"❌ RATIO: {categorized_members / total_members:.2f}x too many" if total_members > 0 else "Cannot calculate ratio")
        
        # Check if there are members in categories that don't exist in main table
        cursor.execute("""
            SELECT mc.member_id, mc.category 
            FROM member_categories mc
            LEFT JOIN members m ON mc.member_id = m.id
            WHERE m.id IS NULL
            LIMIT 20
        """)
        
        orphaned = cursor.fetchall()
        if orphaned:
            print(f"\n❌ Found {len(orphaned)} category entries with no matching member:")
            for member_id, category in orphaned[:10]:
                print(f"   Member ID {member_id} (category: {category}) - NO MATCH in members table")
            if len(orphaned) > 10:
                print(f"   ... and {len(orphaned) - 10} more orphaned entries")
        
        # Get count of all orphaned entries
        cursor.execute("""
            SELECT COUNT(*)
            FROM member_categories mc
            LEFT JOIN members m ON mc.member_id = m.id
            WHERE m.id IS NULL
        """)
        total_orphaned = cursor.fetchone()[0]
        print(f"\nTotal orphaned category entries: {total_orphaned}")
        
        # Check recent category additions
        print(f"\n=== RECENT CATEGORY ADDITIONS ===")
        cursor.execute("""
            SELECT member_id, category, created_at
            FROM member_categories 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        recent = cursor.fetchall()
        for member_id, category, created_at in recent:
            # Get member name if exists
            cursor.execute("SELECT full_name FROM members WHERE id = ?", (member_id,))
            name_result = cursor.fetchone()
            name = name_result[0] if name_result else "❌ MISSING FROM MEMBERS TABLE"
            print(f"   {member_id}: {name} -> {category} ({created_at})")
        
        # Check for members that exist but aren't categorized
        cursor.execute("""
            SELECT COUNT(*)
            FROM members m
            LEFT JOIN member_categories mc ON m.id = mc.member_id
            WHERE mc.member_id IS NULL
        """)
        
        uncategorized_count = cursor.fetchone()[0]
        print(f"\n📊 Members not categorized: {uncategorized_count}")
        
        # Show breakdown by category with member validation
        print(f"\n=== CATEGORY BREAKDOWN WITH VALIDATION ===")
        cursor.execute("""
            SELECT mc.category, COUNT(*) as count,
                   COUNT(m.id) as valid_members,
                   (COUNT(*) - COUNT(m.id)) as orphaned
            FROM member_categories mc
            LEFT JOIN members m ON mc.member_id = m.id
            GROUP BY mc.category
            ORDER BY count DESC
        """)
        
        categories = cursor.fetchall()
        total_valid = 0
        total_orphaned = 0
        
        for category, total_count, valid_count, orphaned_count in categories:
            total_valid += valid_count
            total_orphaned += orphaned_count
            print(f"  {category}: {total_count} total ({valid_count} valid, {orphaned_count} orphaned)")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Valid categorized members: {total_valid}")
        print(f"   Orphaned category entries: {total_orphaned}")
        print(f"   Expected member count: ~{total_members}")
        print(f"   Excess entries to remove: {total_orphaned}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing member counts: {e}")

if __name__ == "__main__":
    analyze_member_discrepancy()