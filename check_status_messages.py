#!/usr/bin/env python3
"""Quick script to check status_message values in database"""
import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check all distinct status messages with "Past" and "Due"
print("\n=== Past Due Status Messages ===")
result = cursor.execute("""
    SELECT DISTINCT status_message, COUNT(*) as count 
    FROM members 
    WHERE status_message LIKE '%Past%Due%' 
    GROUP BY status_message 
    ORDER BY count DESC
""").fetchall()

if result:
    for row in result:
        print(f"  '{row[0]}' - {row[1]} members")
else:
    print("  No past due status messages found")

# Check all distinct status messages (first 20)
print("\n=== All Status Messages (Top 20) ===")
result = cursor.execute("""
    SELECT DISTINCT status_message, COUNT(*) as count 
    FROM members 
    WHERE status_message IS NOT NULL AND status_message != ''
    GROUP BY status_message 
    ORDER BY count DESC
    LIMIT 20
""").fetchall()

for row in result:
    print(f"  '{row[0]}' - {row[1]} members")

# Check if campaign_progress table exists and what's in it
print("\n=== Campaign Progress ===")
try:
    result = cursor.execute("""
        SELECT category, last_processed_member_id, last_processed_index, total_members_in_category 
        FROM campaign_progress 
        WHERE category LIKE '%past_due%'
        ORDER BY last_campaign_date DESC
    """).fetchall()
    
    if result:
        for row in result:
            print(f"  Category: '{row[0]}'")
            print(f"    Last Member ID: {row[1]}")
            print(f"    Last Index: {row[2]}")
            print(f"    Total Members: {row[3]}")
    else:
        print("  No campaign progress found for past_due categories")
except Exception as e:
    print(f"  Campaign progress table error: {e}")

conn.close()
