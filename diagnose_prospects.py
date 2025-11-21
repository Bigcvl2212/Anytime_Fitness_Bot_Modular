"""Quick diagnostic script to check prospects data"""
import sqlite3
from src.services.database_manager import DatabaseManager

db = DatabaseManager()
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check status distribution
print("\n=== Prospects Status Distribution ===")
cursor.execute("SELECT status, COUNT(*) as count FROM prospects GROUP BY status ORDER BY count DESC LIMIT 10")
for row in cursor.fetchall():
    print(f"  Status '{row[0]}': {row[1]:,} prospects")

# Check for active prospects (various status values)
print("\n=== Checking Active Prospects ===")
cursor.execute("SELECT COUNT(*) FROM prospects WHERE status = '1'")
active_count = cursor.fetchone()[0]
print(f"  Status '1' (likely active): {active_count:,} prospects")

# Check recent prospects
print("\n=== Recent Prospects (last 90 days) ===")
cursor.execute("""
    SELECT COUNT(*) FROM prospects 
    WHERE created_at >= datetime('now', '-90 days')
""")
recent_count = cursor.fetchone()[0]
print(f"  Created in last 90 days: {recent_count:,} prospects")

# Check prospects with contact info
print("\n=== Prospects with Contact Info ===")
cursor.execute("SELECT COUNT(*) FROM prospects WHERE email IS NOT NULL OR phone IS NOT NULL")
with_contact = cursor.fetchone()[0]
print(f"  With email or phone: {with_contact:,} prospects")

# Sample active prospect
print("\n=== Sample Active Prospect ===")
cursor.execute("SELECT * FROM prospects WHERE status = '1' LIMIT 1")
columns = [description[0] for description in cursor.description]
row = cursor.fetchone()
if row:
    prospect = dict(zip(columns, row))
    print(f"  ID: {prospect.get('id')}")
    print(f"  Name: {prospect.get('full_name')}")
    print(f"  Email: {prospect.get('email')}")
    print(f"  Status: {prospect.get('status')}")
    print(f"  Created: {prospect.get('created_at')}")
else:
    print("  No active prospects found with status='1'")

# Check what ClubHub typically uses
print("\n=== Checking Typical Active Prospect Criteria ===")
cursor.execute("""
    SELECT COUNT(*) FROM prospects 
    WHERE status != '0' 
    AND (email IS NOT NULL OR phone IS NOT NULL)
    AND created_at >= datetime('now', '-365 days')
""")
likely_active = cursor.fetchone()[0]
print(f"  Non-zero status + contact info + created in last year: {likely_active:,} prospects")

conn.close()
