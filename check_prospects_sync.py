"""
Check recent prospects sync from ClubHub
"""
from src.services.database_manager import DatabaseManager

db = DatabaseManager()

# Check last sync date
result = db.execute_query("""
    SELECT 
        COUNT(*) as total,
        MAX(updated_at) as last_sync
    FROM prospects
""", fetch_all=True)

print("Total prospects in DB:", result[0]['total'] if result else 0)
print("Last sync:", result[0]['last_sync'] if result and result[0]['last_sync'] else 'Never')

# Check how many were updated in last 30 days
recent = db.execute_query("""
    SELECT COUNT(*) as recent_count
    FROM prospects
    WHERE updated_at >= date('now', '-30 days')
""", fetch_all=True)

print("Updated in last 30 days:", recent[0]['recent_count'] if recent else 0)

# Check prospect types/statuses
statuses = db.execute_query("""
    SELECT status, COUNT(*) as count
    FROM prospects
    GROUP BY status
    ORDER BY count DESC
    LIMIT 10
""", fetch_all=True)

print("\nProspect statuses:")
for s in statuses:
    print(f"  Status '{s['status']}': {s['count']}")

# Get sample of recent prospects
recent_prospects = db.execute_query("""
    SELECT prospect_id, first_name, last_name, email, phone, status, updated_at
    FROM prospects
    WHERE updated_at >= date('now', '-30 days')
    ORDER BY updated_at DESC
    LIMIT 10
""", fetch_all=True)

print(f"\nRecent prospects (last {len(recent_prospects)}):")
for p in recent_prospects:
    print(f"  {p.get('prospect_id')}: {p.get('first_name')} {p.get('last_name')} - Status: {p.get('status')} - Updated: {p.get('updated_at')}")
