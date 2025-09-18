import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Get table schema
cursor.execute('PRAGMA table_info(members)')
columns = cursor.fetchall()

print('Members table columns:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

print('\n' + '='*50)

# Check members with NULL agreement_id
cursor.execute('SELECT COUNT(*) FROM members WHERE agreement_id IS NULL')
null_count = cursor.fetchone()[0]
print(f'Members with NULL agreement_id (Collections): {null_count}')

# Check a few examples of NULL agreement_id members
cursor.execute('SELECT first_name, last_name, agreement_id FROM members WHERE agreement_id IS NULL LIMIT 5')
examples = cursor.fetchall()
print('\nExamples of Collections members (NULL agreement_id):')
for row in examples:
    print(f'  {row[0]} {row[1]} - Agreement ID: {row[2]}')

conn.close()