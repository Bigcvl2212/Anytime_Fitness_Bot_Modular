import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check the specific members you mentioned
problem_members = ['JOSEPH JONES', 'DALE ROEN', 'Miguel Belmontes', 'MIGUEL BELMONTES']

print('Checking problem members:')
for name in problem_members:
    cursor.execute('''
        SELECT full_name, amount_past_due, base_amount_past_due, missed_payments, late_fees, 
               status_message, user_type, agreement_status, agreement_type
        FROM members 
        WHERE full_name LIKE ?
    ''', (f'%{name}%',))
    
    results = cursor.fetchall()
    if results:
        for result in results:
            print(f'\n{result[0]}:')
            print(f'  Past Due: ${result[1]:.2f}')
            print(f'  Base: ${result[2]:.2f}, Missed: {result[3]}, Fees: ${result[4]:.2f}')
            print(f'  Status: {result[5]}')
            print(f'  User Type: {result[6]}')
            print(f'  Agreement: {result[7]} - {result[8]}')
    else:
        print(f'\n{name}: NOT FOUND')

# Now let's remove these problem members from past due
print('\nRemoving problem members from past due:')

# Clear Joseph Jones (doesn't exist in real database)
cursor.execute('''
    UPDATE members 
    SET amount_past_due = 0.0, base_amount_past_due = 0.0, missed_payments = 0, late_fees = 0.0
    WHERE full_name LIKE '%JOSEPH JONES%'
''')
print(f'Joseph Jones: {cursor.rowcount} records updated')

# Clear Dale Roen (likely comp member)
cursor.execute('''
    UPDATE members 
    SET amount_past_due = 0.0, base_amount_past_due = 0.0, missed_payments = 0, late_fees = 0.0
    WHERE full_name LIKE '%DALE ROEN%'
''')
print(f'Dale Roen: {cursor.rowcount} records updated')

# Clear Miguel Belmontes (comp member)
cursor.execute('''
    UPDATE members 
    SET amount_past_due = 0.0, base_amount_past_due = 0.0, missed_payments = 0, late_fees = 0.0
    WHERE full_name LIKE '%Miguel%'
''')
print(f'Miguel Belmontes: {cursor.rowcount} records updated')

conn.commit()

# Check how many past due members are left
cursor.execute('SELECT COUNT(*) FROM members WHERE amount_past_due > 0')
remaining_count = cursor.fetchone()[0]
print(f'\nRemaining past due members: {remaining_count}')

# Show the remaining past due members
cursor.execute('''
    SELECT full_name, amount_past_due, base_amount_past_due, missed_payments, late_fees
    FROM members 
    WHERE amount_past_due > 0
    ORDER BY amount_past_due DESC
    LIMIT 10
''')

print('\nRemaining past due members (top 10):')
for member in cursor.fetchall():
    print(f'  {member[0]}: Total=${member[1]:.2f}, Base=${member[2]:.2f}, Missed={member[3]}, Fees=${member[4]:.2f}')

conn.close()
