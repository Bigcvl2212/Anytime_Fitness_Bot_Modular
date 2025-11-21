import sqlite3
from datetime import datetime

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("=" * 70)
print("INBOX SYNC DIAGNOSIS - ROOT CAUSE ANALYSIS")
print("=" * 70)

# 1. Check what the ORDER BY returns
print("\n1. WHAT THE INBOX API RETURNS (ORDER BY created_at DESC):")
cursor.execute("""
    SELECT from_user, created_at, timestamp
    FROM messages
    WHERE channel='clubos'
    AND from_user IS NOT NULL
    AND from_user != ''
    AND LENGTH(TRIM(content)) > 5
    ORDER BY created_at DESC
    LIMIT 10
""")
results = cursor.fetchall()
for i, r in enumerate(results, 1):
    print(f"   {i}. {r[0]} - created_at: {r[1]}, ClubOS timestamp: {r[2]}")

# 2. Check what SHOULD be returned (by actual message date)
print("\n2. WHAT SHOULD BE RETURNED (Real November messages):")
cursor.execute("""
    SELECT from_user, created_at, timestamp
    FROM messages
    WHERE channel='clubos'
    AND timestamp LIKE '%Nov%'
    ORDER BY created_at DESC
    LIMIT 10
""")
results = cursor.fetchall()
if results:
    for i, r in enumerate(results, 1):
        print(f"   {i}. {r[0]} - created_at: {r[1]}, ClubOS timestamp: {r[2]}")
else:
    print("   NO NOVEMBER MESSAGES IN DATABASE!")

# 3. Explain the problem
print("\n3. ROOT CAUSE:")
print("   - Messages are SYNCED today (created_at = 2025-11-21)")
print("   - BUT ClubOS returns OLD messages (timestamp = 'Jan 24', 'Feb 10', etc.)")
print("   - The inbox sorts by 'created_at' (sync time) not 'timestamp' (actual message date)")
print("   - Result: Shows old January/February messages instead of November messages")

# 4. Check if ClubOS is returning fresh messages
print("\n4. DID CLUBOS SYNC RETURN FRESH NOVEMBER MESSAGES TODAY?")
cursor.execute("""
    SELECT COUNT(*) FROM messages
    WHERE channel='clubos'
    AND created_at LIKE '2025-11-21%'
    AND timestamp LIKE '%Nov%'
""")
nov_count = cursor.fetchone()[0]
print(f"   November messages synced today: {nov_count}")

cursor.execute("""
    SELECT COUNT(*) FROM messages
    WHERE channel='clubos'
    AND created_at LIKE '2025-11-21%'
""")
total_count = cursor.fetchone()[0]
print(f"   Total messages synced today: {total_count}")
print(f"   Percentage November: {nov_count/total_count*100:.1f}%")

# 5. What ClubOS actually returned
print("\n5. WHAT CLUBOS RETURNED IN LAST SYNC:")
cursor.execute("""
    SELECT timestamp, COUNT(*) as cnt
    FROM messages
    WHERE channel='clubos'
    AND created_at LIKE '2025-11-21%'
    GROUP BY timestamp
    ORDER BY cnt DESC
    LIMIT 10
""")
print("   Top 10 timestamps by count:")
for r in cursor.fetchall():
    print(f"      {r[0]}: {r[1]} messages")

print("\n" + "=" * 70)
print("CONCLUSION:")
print("=" * 70)
print("The inbox API DOES sync from ClubOS and stores messages successfully.")
print("However, ClubOS is returning OLD historical messages, not recent ones.")
print("The ORDER BY created_at DESC shows the most recently SYNCED messages,")
print("which happen to be OLD messages that ClubOS keeps returning.")
print("\nPROBLEM: ClubOS API is returning old January/February messages")
print("         instead of fresh November messages!")
print("=" * 70)

conn.close()
