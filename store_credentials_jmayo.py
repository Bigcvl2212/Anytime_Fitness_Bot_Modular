#!/usr/bin/env python3
"""
Store ClubHub credentials for j.mayo
"""
import sqlite3
import json

# Credentials
manager_id = "ef8de92f-f6b5-43"
credentials = {
    "clubos_username": "j.mayo",
    "clubos_password": "W-!R6Bv9FgPnuB4",
    "clubhub_email": "mayo.jeremy2212@gmail.com",
    "clubhub_password": "fygxy9-sybses-suvtYc"
}

print("Storing credentials for j.mayo...")

# Store in database
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check if credentials table exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS manager_credentials (
        manager_id TEXT PRIMARY KEY,
        clubos_username TEXT,
        clubos_password TEXT,
        clubhub_email TEXT,
        clubhub_password TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insert or update credentials
cursor.execute("""
    INSERT OR REPLACE INTO manager_credentials
    (manager_id, clubos_username, clubos_password, clubhub_email, clubhub_password, updated_at)
    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
""", (
    manager_id,
    credentials['clubos_username'],
    credentials['clubos_password'],
    credentials['clubhub_email'],
    credentials['clubhub_password']
))

conn.commit()
conn.close()

print(f"Credentials stored successfully for manager_id: {manager_id}")
print(f"  ClubOS Username: {credentials['clubos_username']}")
print(f"  ClubHub Email: {credentials['clubhub_email']}")
print("\nYou can now log in and your clubs will be loaded from ClubHub!")
