import sqlite3

# Investigate duplicate members in the database
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("🔍 Database Duplicate Analysis:")
print("=" * 60)

# 1. Total member count
cursor.execute('SELECT COUNT(*) FROM members')
total_count = cursor.fetchone()[0]
print(f"📊 Total members in database: {total_count}")

# 2. Check for duplicate prospect_ids
cursor.execute('''
    SELECT prospect_id, COUNT(*) as count 
    FROM members 
    WHERE prospect_id IS NOT NULL 
    GROUP BY prospect_id 
    HAVING COUNT(*) > 1 
    ORDER BY count DESC
''')
duplicate_prospect_ids = cursor.fetchall()
print(f"\n🔄 Duplicate prospect_ids: {len(duplicate_prospect_ids)}")
if duplicate_prospect_ids:
    print("Top duplicates by prospect_id:")
    for prospect_id, count in duplicate_prospect_ids[:10]:
        print(f"  {prospect_id}: {count} entries")

# 3. Check for duplicate emails
cursor.execute('''
    SELECT email, COUNT(*) as count 
    FROM members 
    WHERE email IS NOT NULL AND email != '' 
    GROUP BY email 
    HAVING COUNT(*) > 1 
    ORDER BY count DESC
''')
duplicate_emails = cursor.fetchall()
print(f"\n📧 Duplicate emails: {len(duplicate_emails)}")
if duplicate_emails:
    print("Top duplicates by email:")
    for email, count in duplicate_emails[:10]:
        print(f"  {email}: {count} entries")

# 4. Check for duplicate names
cursor.execute('''
    SELECT first_name, last_name, COUNT(*) as count 
    FROM members 
    WHERE first_name IS NOT NULL AND last_name IS NOT NULL 
    GROUP BY first_name, last_name 
    HAVING COUNT(*) > 1 
    ORDER BY count DESC
''')
duplicate_names = cursor.fetchall()
print(f"\n👥 Duplicate names: {len(duplicate_names)}")
if duplicate_names:
    print("Top duplicates by name:")
    for first_name, last_name, count in duplicate_names[:10]:
        print(f"  {first_name} {last_name}: {count} entries")

# 5. Check category distribution
categories_query = '''
    SELECT 
        SUM(CASE WHEN status_message = 'Member is in good standing' THEN 1 ELSE 0 END) as green,
        SUM(CASE WHEN status_message IN ('Past Due 6-30 days', 'Invalid Billing Information.', 'Invalid/Bad Address information.', 'Member is pending cancel', 'Member will expire within 30 days.') THEN 1 ELSE 0 END) as past_due,
        SUM(CASE WHEN status_message = 'Comp Member' THEN 1 ELSE 0 END) as comp,
        SUM(CASE WHEN status_message = 'Pay Per Visit Member' THEN 1 ELSE 0 END) as ppv,
        SUM(CASE WHEN prospect_id IN ('64309309', '55867562', '50909888', '62716557', '52750389') THEN 1 ELSE 0 END) as staff,
        SUM(CASE WHEN agreement_id IS NULL AND (status_message IN ('Past Due 6-30 days', 'Past Due more than 30 days.', 'Invalid Billing Information.', 'Invalid/Bad Address information.') OR amount_past_due > 0) THEN 1 ELSE 0 END) as collections,
        SUM(CASE WHEN status_message IN ('Expired') OR status_message IS NULL THEN 1 ELSE 0 END) as inactive
    FROM members
'''

cursor.execute(categories_query)
category_counts = cursor.fetchone()
categories = ['green', 'past_due', 'comp', 'ppv', 'staff', 'collections', 'inactive']

print(f"\n📈 Category Distribution:")
total_categorized = 0
for i, category in enumerate(categories):
    count = category_counts[i]
    total_categorized += count
    print(f"  {category.upper()}: {count}")

print(f"\nTotal categorized: {total_categorized}")
print(f"Total in database: {total_count}")
print(f"Difference: {total_count - total_categorized}")

# 6. Find uncategorized members
cursor.execute('''
    SELECT first_name, last_name, status_message, prospect_id
    FROM members 
    WHERE status_message NOT IN (
        'Member is in good standing',
        'Past Due 6-30 days', 
        'Invalid Billing Information.',
        'Invalid/Bad Address information.',
        'Member is pending cancel',
        'Member will expire within 30 days.',
        'Comp Member',
        'Pay Per Visit Member',
        'Expired'
    )
    AND status_message IS NOT NULL
    AND prospect_id NOT IN ('64309309', '55867562', '50909888', '62716557', '52750389')
    LIMIT 10
''')

uncategorized = cursor.fetchall()
print(f"\n❓ Uncategorized members (sample):")
for member in uncategorized:
    print(f"  {member[0]} {member[1]} - Status: '{member[2]}' - ID: {member[3]}")

conn.close()