#!/usr/bin/env python3

import sqlite3
from collections import Counter

def check_duplicates():
    """Check for duplicate entries in member_categories table"""
    
    db_path = "gym_bot.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== CHECKING FOR DUPLICATES IN MEMBER_CATEGORIES ===")
        
        # Check if there are multiple entries for the same member_id
        cursor.execute("""
            SELECT member_id, COUNT(*) as count
            FROM member_categories 
            GROUP BY member_id 
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)
        
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f"❌ Found {len(duplicates)} members with duplicate category entries:")
            
            for member_id, count in duplicates[:10]:  # Show first 10
                print(f"   Member ID {member_id}: {count} entries")
                
                # Show what categories they have
                cursor.execute("""
                    SELECT category, created_at 
                    FROM member_categories 
                    WHERE member_id = ? 
                    ORDER BY created_at
                """, (member_id,))
                
                categories = cursor.fetchall()
                for category, created_at in categories:
                    print(f"      - {category} (created: {created_at})")
                print()
            
            if len(duplicates) > 10:
                print(f"... and {len(duplicates) - 10} more members with duplicates")
        else:
            print("✅ No duplicate member_id entries found")
        
        print("\n=== CATEGORY BREAKDOWN WITH DUPLICATES ===")
        
        # Get total counts including duplicates
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM member_categories 
            GROUP BY category 
            ORDER BY count DESC
        """)
        
        category_counts = cursor.fetchall()
        total_entries = sum(count for _, count in category_counts)
        
        print("Current counts (with duplicates):")
        for category, count in category_counts:
            print(f"  {category}: {count}")
        
        print(f"\nTotal entries: {total_entries}")
        
        # Get unique member count
        cursor.execute("SELECT COUNT(DISTINCT member_id) FROM member_categories")
        unique_members = cursor.fetchone()[0]
        
        print(f"Unique members with categories: {unique_members}")
        print(f"Duplicate entries: {total_entries - unique_members}")
        
        print("\n=== SAMPLE DUPLICATE ANALYSIS ===")
        
        if duplicates:
            # Analyze first few duplicates
            for member_id, count in duplicates[:3]:
                cursor.execute("""
                    SELECT m.full_name, m.agreement_type, m.amount_past_due
                    FROM members m
                    WHERE m.member_id = ?
                """, (member_id,))
                
                member_info = cursor.fetchone()
                if member_info:
                    name, agreement_type, amount_past_due = member_info
                    print(f"Member: {name} (ID: {member_id})")
                    print(f"  Agreement: {agreement_type}, Past Due: ${amount_past_due or 0}")
                    
                    cursor.execute("""
                        SELECT category, created_at
                        FROM member_categories 
                        WHERE member_id = ?
                        ORDER BY created_at
                    """, (member_id,))
                    
                    entries = cursor.fetchall()
                    print(f"  Categories ({len(entries)} total):")
                    for category, created_at in entries:
                        print(f"    - {category} ({created_at})")
                    print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking duplicates: {e}")

if __name__ == "__main__":
    check_duplicates()