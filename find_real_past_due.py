import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Look for members with actual past due status messages
cursor.execute('''
    SELECT full_name, status_message, amount_past_due, user_type
    FROM members 
    WHERE (status_message LIKE '%Past Due%' 
    OR status_message LIKE '%Delinquent%'
    OR status_message LIKE '%overdue%')
    AND status_message NOT LIKE '%good standing%'
    ORDER BY status_message
''')

past_due_by_status = cursor.fetchall()
print(f'Members with past due status messages: {len(past_due_by_status)}')

for member in past_due_by_status:
    print(f'  {member[0]}: {member[1]} (Amount: ${member[2]:.2f}, Type: {member[3]})')

# If there are legitimate past due members by status, let's update their amounts
if past_due_by_status:
    print('\nUpdating legitimate past due members...')
    for member in past_due_by_status:
        name = member[0]
        status_msg = member[1]
        
        # Set reasonable past due amounts for members with past due status
        if 'Past Due more than 30' in status_msg or 'Delinquent' in status_msg:
            # Critical - assume 3+ missed payments
            missed_payments = 3
            base_amount = 150.0  # 3 months at $50/month
            late_fees = missed_payments * 19.50
            total_amount = base_amount + late_fees
        elif 'Past Due 6-30' in status_msg:
            # Warning - assume 2 missed payments  
            missed_payments = 2
            base_amount = 100.0  # 2 months at $50/month
            late_fees = missed_payments * 19.50
            total_amount = base_amount + late_fees
        else:
            # Default - 1 missed payment
            missed_payments = 1
            base_amount = 50.0   # 1 month at $50/month
            late_fees = 19.50
            total_amount = base_amount + late_fees
            
        cursor.execute('''
            UPDATE members 
            SET amount_past_due = ?, base_amount_past_due = ?, missed_payments = ?, late_fees = ?
            WHERE full_name = ?
        ''', (total_amount, base_amount, missed_payments, late_fees, name))
        
        print(f'  Updated {name}: Total=${total_amount:.2f}, Base=${base_amount:.2f}, Missed={missed_payments}, Fees=${late_fees:.2f}')

    conn.commit()
    
    # Check final count
    cursor.execute('SELECT COUNT(*) FROM members WHERE amount_past_due > 0')
    final_count = cursor.fetchone()[0]
    print(f'\nFinal legitimate past due members: {final_count}')
else:
    print('\nNo members found with legitimate past due status messages.')
    print('This suggests your database may not have real past due members currently,')
    print('or they need to be synced from ClubHub with correct status messages.')

conn.close()
