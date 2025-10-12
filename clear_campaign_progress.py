#!/usr/bin/env python3
"""Quick script to manually clear campaign progress for testing"""
import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Show current campaign progress
print("\n=== Current Campaign Progress ===")
result = cursor.execute("""
    SELECT category, last_processed_member_id, last_processed_index, total_members_in_category, last_campaign_date
    FROM campaign_progress 
    ORDER BY last_campaign_date DESC
""").fetchall()

if result:
    for row in result:
        print(f"  Category: {row[0]}")
        print(f"    Last Member: {row[1]}")
        print(f"    Last Index: {row[2]}")
        print(f"    Total: {row[3]}")
        print(f"    Date: {row[4]}")
        print()
else:
    print("  No campaign progress found")

# Clear past_due_6_30 progress
print("\n=== Clearing past_due_6_30 Campaign Progress ===")
cursor.execute("DELETE FROM campaign_progress WHERE category = 'past_due_6_30'")
conn.commit()
print("✅ Cleared past_due_6_30 campaign progress")

# Verify
result = cursor.execute("""
    SELECT COUNT(*) FROM campaign_progress WHERE category = 'past_due_6_30'
""").fetchone()
print(f"✅ Remaining past_due_6_30 entries: {result[0]}")

# Check how many members should be available
print("\n=== Available Members ===")
result = cursor.execute("""
    SELECT COUNT(*) FROM members WHERE status_message = 'Past Due 6-30 days'
""").fetchone()
print(f"📊 Total 'Past Due 6-30 days' members: {result[0]}")

conn.close()
print("\n✅ Done! The campaign should now find all 15 members.")
