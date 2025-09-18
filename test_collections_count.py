import sqlite3

# Test the corrected collections functionality
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("🔍 Analyzing NULL agreement_id members:")
print("=" * 50)

# Check ALL members with NULL agreement_id
cursor.execute('SELECT first_name, last_name, status_message, amount_past_due FROM members WHERE agreement_id IS NULL')
null_members = cursor.fetchall()

print(f"All members with NULL agreement_id: {len(null_members)}")
for member in null_members:
    past_due = member[3] or 0
    print(f"  {member[0]} {member[1]} - Status: {member[2]} - Past Due: ${past_due}")

print("\n" + "=" * 50)

# Test CORRECTED collections count (past due AND NULL agreement_id)
cursor.execute("""
    SELECT COUNT(*) FROM members
    WHERE agreement_id IS NULL 
    AND (status_message IN (
        'Past Due 6-30 days',
        'Past Due more than 30 days.',
        'Invalid Billing Information.',
        'Invalid/Bad Address information.'
    ) OR amount_past_due > 0)
""")
collections_count = cursor.fetchone()[0]

# Test CORRECTED collections members
cursor.execute("""
    SELECT first_name, last_name, status_message, amount_past_due FROM members
    WHERE agreement_id IS NULL 
    AND (status_message IN (
        'Past Due 6-30 days',
        'Past Due more than 30 days.',
        'Invalid Billing Information.',
        'Invalid/Bad Address information.'
    ) OR amount_past_due > 0)
""")
collections_members = cursor.fetchall()

print(f"✅ CORRECTED Collections Results:")
print(f"📊 True Collections Count (past due + NULL agreement): {collections_count}")
print(f"👥 True Collections Members:")

for i, member in enumerate(collections_members):
    past_due = member[3] or 0
    print(f"  {i+1}. {member[0]} {member[1]} - Status: {member[2]} - Past Due: ${past_due}")

print(f"\n🎯 Collections tab will now show {collections_count} members (only past due + NULL agreement)")
print("✅ Logic corrected - month-to-month/expired members excluded!")

conn.close()