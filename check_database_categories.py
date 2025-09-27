#!/usr/bin/env python3
"""
Quick script to check database state and member categorization
"""
import sqlite3
import os

# Database path
db_path = "gym_bot.db"

if not os.path.exists(db_path):
    print(f"❌ Database not found: {db_path}")
    exit(1)

print(f"🔍 Checking database: {db_path}")
print("=" * 50)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check members table
    cursor.execute("SELECT COUNT(*) FROM members")
    member_count = cursor.fetchone()[0]
    print(f"👥 Total members in database: {member_count}")
    
    # Check member_categories table
    cursor.execute("SELECT COUNT(*) FROM member_categories")
    category_count = cursor.fetchone()[0]
    print(f"📊 Total categorized members: {category_count}")
    
    if category_count > 0:
        # Show category breakdown
        cursor.execute("SELECT category, COUNT(*) FROM member_categories GROUP BY category ORDER BY COUNT(*) DESC")
        categories = cursor.fetchall()
        print("\n📋 Category Breakdown:")
        for category, count in categories:
            print(f"  {category}: {count}")
    else:
        print("⚠️ No member categories found - sync may still be running")
    
    # Check status message distribution
    print("\n💬 Status Message Distribution:")
    cursor.execute("""
        SELECT status_message, COUNT(*) as count 
        FROM members 
        WHERE status_message IS NOT NULL 
        GROUP BY status_message 
        ORDER BY count DESC 
        LIMIT 10
    """)
    status_messages = cursor.fetchall()
    for status, count in status_messages:
        print(f"  {status}: {count}")
    
    # Check past due members using heuristics
    print("\n💰 Past Due Analysis:")
    cursor.execute("""
        SELECT COUNT(*) FROM members
        WHERE status_message IN ('Past Due 6-30 days', 'Past Due more than 30 days.')
    """)
    past_due_count = cursor.fetchone()[0]
    print(f"  Past Due (heuristics): {past_due_count}")
    
    # Check green members using heuristics  
    cursor.execute("""
        SELECT COUNT(*) FROM members
        WHERE status_message IN ('Member is in good standing', 'In good standing')
    """)
    green_count = cursor.fetchone()[0]
    print(f"  Green (heuristics): {green_count}")
    
    # Check last update times
    cursor.execute("SELECT MAX(updated_at) FROM members")
    last_update = cursor.fetchone()[0]
    print(f"\n⏰ Last member update: {last_update}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Database error: {e}")

print("\n✅ Database check complete")