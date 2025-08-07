#!/usr/bin/env python3
"""
Check prospect IDs for Jordan and Dennis
"""

import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("=== PROSPECT ID INVESTIGATION ===")

# Check Jordan and Dennis prospect IDs
cursor.execute("SELECT id, first_name, last_name, prospect_id FROM members WHERE first_name LIKE '%Jordan%' OR first_name LIKE '%Dennis%'")
rows = cursor.fetchall()

print("Members with prospect IDs:")
for row in rows:
    clubhub_id, first_name, last_name, prospect_id = row
    print(f"ClubHub ID: {clubhub_id}, Name: {first_name} {last_name}, Prospect ID: {prospect_id}")

# Check if Jordan's prospect ID matches his ClubOS ID from funding cache
print(f"\n=== JORDAN'S ID COMPARISON ===")
cursor.execute("SELECT member_name, clubos_member_id FROM funding_status_cache WHERE member_name LIKE '%Jordan Krueger%'")
jordan_cache = cursor.fetchall()

if jordan_cache:
    cache_name, cache_clubos_id = jordan_cache[0]
    print(f"Jordan's cached ClubOS ID: {cache_clubos_id}")
    
    # Find Jordan's prospect ID
    cursor.execute("SELECT prospect_id FROM members WHERE first_name='Jordan' AND last_name='Krueger'")
    jordan_prospect = cursor.fetchone()
    
    if jordan_prospect:
        prospect_id = jordan_prospect[0]
        print(f"Jordan's prospect ID: {prospect_id}")
        
        if str(prospect_id) == str(cache_clubos_id):
            print("✅ MATCH! Prospect ID = ClubOS ID")
        else:
            print("❌ No match between prospect ID and ClubOS ID")
    else:
        print("❌ Jordan not found in members table")
else:
    print("❌ Jordan not found in funding cache")

conn.close()
