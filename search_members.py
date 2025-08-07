#!/usr/bin/env python3
"""
Search for Jordan and Dennis in members table
"""

import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("=== SEARCHING FOR JORDAN AND DENNIS ===")

# Search broadly
cursor.execute("SELECT id, first_name, last_name FROM members WHERE first_name LIKE '%Jordan%' OR last_name LIKE '%Krueger%' OR first_name LIKE '%Dennis%' OR last_name LIKE '%Rost%'")
rows = cursor.fetchall()

print(f"Potential matches in members table:")
for row in rows:
    print(f"  ID: {row[0]}, Name: {row[1]} {row[2]}")

# Also check total member count
cursor.execute("SELECT COUNT(*) FROM members")
total = cursor.fetchone()[0]
print(f"\nTotal members in database: {total}")

# Check if ClubHub IDs 44871105 (Jordan) and 65828815 (Dennis) exist
print(f"\n=== CHECKING SPECIFIC CLUBHUB IDs ===")
for name, clubhub_id in [("Jordan Krueger", 44871105), ("Dennis Rost", 65828815)]:
    cursor.execute("SELECT id, first_name, last_name FROM members WHERE id = ?", (clubhub_id,))
    row = cursor.fetchone()
    if row:
        print(f"✅ Found {name} with ClubHub ID {clubhub_id}: {row[1]} {row[2]}")
    else:
        print(f"❌ ClubHub ID {clubhub_id} for {name} not found in members table")

conn.close()
