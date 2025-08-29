#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check for Mark Benzinger
cursor.execute("SELECT id, guid, full_name FROM members WHERE full_name LIKE '%Mark%' OR full_name LIKE '%Benzinger%'")
mark_results = cursor.fetchall()
print(f"Mark Benzinger records: {mark_results}")

# Check total members with GUID
cursor.execute("SELECT COUNT(*) FROM members WHERE guid IS NOT NULL")
guid_count = cursor.fetchone()[0]
print(f"Total members with GUID: {guid_count}")

# Get some sample members with GUID
cursor.execute("SELECT id, guid, full_name FROM members WHERE guid IS NOT NULL LIMIT 5")
sample_members = cursor.fetchall()
print(f"Sample members with GUID: {sample_members}")

# Check training clients for Mark Benzinger ID
cursor.execute("SELECT clubos_member_id, member_name FROM training_clients WHERE clubos_member_id = '125814462' OR member_name LIKE '%Mark%' OR member_name LIKE '%Benzinger%'")
training_results = cursor.fetchall()
print(f"Training clients with Mark info: {training_results}")

conn.close()
