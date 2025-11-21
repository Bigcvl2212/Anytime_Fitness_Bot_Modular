"""Investigate why some past due members don't have agreement IDs"""
import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("=" * 80)
print("INVESTIGATING MISSING AGREEMENT IDs")
print("=" * 80)
print("")

# Get past due members without agreement IDs
cursor.execute("""
    SELECT
        first_name || ' ' || last_name as name,
        prospect_id,
        guid,
        amount_past_due,
        status_message
    FROM members
    WHERE (status_message LIKE '%Past Due%' OR amount_past_due > 0)
    AND amount_past_due > 0
    AND (agreement_id IS NULL OR agreement_id = '' OR agreement_id = 'N/A')
    ORDER BY amount_past_due DESC
    LIMIT 10
""")

print("Past Due Members WITHOUT Agreement IDs:")
print("-" * 80)
for name, prospect_id, guid, past_due, status in cursor.fetchall():
    print(f"Name: {name}")
    print(f"  Prospect ID: {prospect_id if prospect_id else 'NONE'}")
    print(f"  Member GUID: {guid if guid else 'NONE'}")
    print(f"  Past Due: ${past_due:.2f}")
    print(f"  Status: {status}")
    print("")

# Check: Do members WITH agreement IDs have any pattern?
cursor.execute("""
    SELECT
        first_name || ' ' || last_name as name,
        prospect_id,
        guid,
        agreement_id,
        amount_past_due
    FROM members
    WHERE (status_message LIKE '%Past Due%' OR amount_past_due > 0)
    AND amount_past_due > 0
    AND agreement_id IS NOT NULL
    AND agreement_id != ''
    AND agreement_id != 'N/A'
    ORDER BY amount_past_due DESC
    LIMIT 5
""")

print("=" * 80)
print("Past Due Members WITH Agreement IDs (for comparison):")
print("-" * 80)
for name, prospect_id, guid, agreement_id, past_due in cursor.fetchall():
    print(f"Name: {name}")
    print(f"  Prospect ID: {prospect_id if prospect_id else 'NONE'}")
    print(f"  Member GUID: {guid if guid else 'NONE'}")
    print(f"  Agreement ID: {agreement_id}")
    print(f"  Past Due: ${past_due:.2f}")
    print("")

conn.close()

print("=" * 80)
print("POSSIBLE REASONS FOR MISSING AGREEMENT IDs:")
print("=" * 80)
print("1. ClubHub member details endpoint doesn't have agreement IDs for these members")
print("2. These members may have inactive or cancelled agreements")
print("3. Agreement data might be stored in a separate endpoint (e.g., /members/{id}/agreement)")
print("4. Some members might be on hold or have special status")
print("")
print("NEXT STEP: Try fetching from the member agreement endpoint")
