"""
Force re-sync of ClubOS messages with corrected timestamp parser.

This script:
1. Clears the messages table
2. Triggers a fresh sync from ClubOS
3. Verifies timestamps are being extracted correctly
"""

import sqlite3
import requests
import time

print("\n" + "="*60)
print("FORCE RE-SYNC OF CLUBOS MESSAGES")
print("="*60)

# Step 1: Clear messages table
print("\n[1/3] Clearing old messages from database...")
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

before_count = cursor.execute('SELECT COUNT(*) FROM messages WHERE channel = "clubos"').fetchone()[0]
print(f"   Found {before_count} existing ClubOS messages")

cursor.execute('DELETE FROM messages WHERE channel = "clubos"')
conn.commit()
print("   ✅ Messages table cleared")

conn.close()

# Step 2: Trigger sync from ClubOS
print("\n[2/3] Triggering sync from ClubOS API...")
print("   NOTE: Flask must be running for this to work!")

try:
    response = requests.post(
        'http://localhost:5000/api/messages/sync',
        json={},
        headers={'Content-Type': 'application/json'},
        timeout=120  # 2 minute timeout for large sync
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Sync complete: {data.get('total_messages', 0)} messages fetched")
    else:
        print(f"   ❌ Sync failed: HTTP {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
        
except requests.exceptions.ConnectionError:
    print("   ❌ ERROR: Could not connect to Flask server!")
    print("   Make sure Flask is running: python run_dashboard.py")
    exit(1)
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    exit(1)

# Step 3: Verify timestamps
print("\n[3/3] Verifying timestamp extraction...")

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Get sample of messages
messages = cursor.execute('''
    SELECT from_user, timestamp, content 
    FROM messages 
    WHERE channel = "clubos" 
    ORDER BY ROWID ASC 
    LIMIT 10
''').fetchall()

after_count = cursor.execute('SELECT COUNT(*) FROM messages WHERE channel = "clubos"').fetchone()[0]
print(f"\n   Total messages in database: {after_count}")

# Check timestamp format
iso_timestamps = cursor.execute('''
    SELECT COUNT(*) 
    FROM messages 
    WHERE channel = "clubos" 
    AND timestamp LIKE "____-__-__T__:__:__%"
''').fetchone()[0]

human_timestamps = after_count - iso_timestamps

print(f"   ISO timestamps (fallback): {iso_timestamps}")
print(f"   Human timestamps (from ClubOS): {human_timestamps}")

if human_timestamps > 0:
    print("\n   ✅ SUCCESS! Parser is extracting timestamps from ClubOS HTML")
    print("\n   Sample of newest messages:")
    for i, msg in enumerate(messages, 1):
        print(f"   {i}. {msg[0]} | {msg[1]} | {msg[2][:50]}...")
else:
    print("\n   ❌ WARNING: All timestamps are ISO format (fallback)")
    print("   Parser may not be finding the sibling <div class='message-options'> element")
    print("\n   Sample messages:")
    for i, msg in enumerate(messages, 1):
        print(f"   {i}. {msg[0]} | {msg[1]} | {msg[2][:50]}...")

conn.close()

print("\n" + "="*60)
print("RE-SYNC COMPLETE")
print("="*60)
print("\nNext step: Refresh the /messaging page in your browser to see updated inbox")
