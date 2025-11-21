"""Check how many past due members have agreement IDs"""
import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Total past due members
cursor.execute("""
    SELECT COUNT(*) FROM members
    WHERE (status_message LIKE '%Past Due%' OR amount_past_due > 0)
    AND amount_past_due > 0
""")
total = cursor.fetchone()[0]

# Past due members with agreement IDs
cursor.execute("""
    SELECT COUNT(*) FROM members
    WHERE (status_message LIKE '%Past Due%' OR amount_past_due > 0)
    AND amount_past_due > 0
    AND agreement_id IS NOT NULL
    AND agreement_id != ''
    AND agreement_id != 'N/A'
""")
with_agreements = cursor.fetchone()[0]

print("=" * 80)
print("AGREEMENT ID STATUS FOR PAST DUE MEMBERS")
print("=" * 80)
print(f"Past due members with agreement IDs: {with_agreements}/{total} ({with_agreements/total*100:.1f}%)")
print("")

# Show all past due members
cursor.execute("""
    SELECT
        first_name || ' ' || last_name as name,
        agreement_id,
        amount_past_due
    FROM members
    WHERE (status_message LIKE '%Past Due%' OR amount_past_due > 0)
    AND amount_past_due > 0
    ORDER BY amount_past_due DESC
""")

print("All Past Due Members:")
print("-" * 80)
for name, agreement_id, past_due in cursor.fetchall():
    status = "YES" if agreement_id and agreement_id != 'N/A' else "NO"
    agreement_display = agreement_id if agreement_id and agreement_id != 'N/A' else 'N/A'
    print(f"{name:35} | Agreement: {agreement_display:15} | ${past_due:8.2f} | {status}")

conn.close()
