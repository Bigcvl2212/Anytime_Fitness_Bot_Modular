import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("📊 Updated Category Counts:")
print("=" * 40)

# Test the updated counts with all status messages included
categories_query = '''
    SELECT 
        SUM(CASE WHEN status_message IN ('Member is in good standing', 'In good standing') THEN 1 ELSE 0 END) as green,
        SUM(CASE WHEN status_message IN ('Past Due 6-30 days', 'Past Due more than 30 days.', 'Invalid Billing Information.', 'Invalid/Bad Address information.', 'Member is pending cancel', 'Member will expire within 30 days.') THEN 1 ELSE 0 END) as past_due,
        SUM(CASE WHEN status_message = 'Comp Member' THEN 1 ELSE 0 END) as comp,
        SUM(CASE WHEN status_message = 'Pay Per Visit Member' THEN 1 ELSE 0 END) as ppv,
        SUM(CASE WHEN status_message IN ('Staff Member', 'Staff member') THEN 1 ELSE 0 END) as staff,
        SUM(CASE WHEN agreement_id IS NULL AND (status_message IN ('Past Due 6-30 days', 'Past Due more than 30 days.', 'Invalid Billing Information.', 'Invalid/Bad Address information.') OR amount_past_due > 0) THEN 1 ELSE 0 END) as collections,
        SUM(CASE WHEN status_message IN ('Expired', 'Account has been cancelled.', 'Sent to Collections') OR status_message IS NULL THEN 1 ELSE 0 END) as inactive
    FROM members
'''

cursor.execute(categories_query)
category_counts = cursor.fetchone()
categories = ['green', 'past_due', 'comp', 'ppv', 'staff', 'collections', 'inactive']

total_categorized = 0
for i, category in enumerate(categories):
    count = category_counts[i]
    total_categorized += count
    print(f"  {category.upper()}: {count}")

print(f"\nTotal categorized: {total_categorized}")
print(f"Total in database: 531")
print(f"Difference: {531 - total_categorized}")

if 531 - total_categorized == 0:
    print("✅ All members are now properly categorized!")
else:
    print("❌ Still have uncategorized members")

conn.close()