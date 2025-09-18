#!/usr/bin/env python3
"""
Add missing contact info for Rashida Hull and Mindy Feilbach
"""

import sqlite3

def update_contact_info():
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    print('=== UPDATING RASHIDA HULL CONTACT INFO ===')
    # Update Rashida Hull
    cursor.execute('''UPDATE training_clients 
                      SET email = ?, phone = ? 
                      WHERE member_id = ? AND first_name = ? AND last_name = ?''', 
                      ('hullrashida7@gmail.com', '(920) 970-1585', '191018939', 'Rashida', 'Hull'))
    
    print(f"Updated {cursor.rowcount} rows for Rashida Hull")
    
    print('\n=== UPDATING MINDY FEILBACH CONTACT INFO ===')
    # Update Mindy Feilbach  
    cursor.execute('''UPDATE training_clients 
                      SET email = ?, phone = ? 
                      WHERE member_id = ? AND first_name = ? AND last_name = ?''', 
                      ('feilbach418mindy@gmail.com', '+1 (920) 517-3554', '163020442', 'Mindy', 'Feilbach'))
    
    print(f"Updated {cursor.rowcount} rows for Mindy Feilbach")
    
    # Commit the changes
    conn.commit()
    
    print('\n=== VERIFICATION ===')
    # Verify the updates
    cursor.execute('''SELECT member_id, member_name, first_name, last_name, email, phone, past_due_amount, payment_status 
                      FROM training_clients 
                      WHERE member_id IN ('191018939', '163020442')
                      ORDER BY member_name''')
    
    results = cursor.fetchall()
    for row in results:
        print(f"ID: {row[0]} | Name: {row[1]} | First: {row[2]} | Last: {row[3]} | Email: {row[4]} | Phone: {row[5]} | Past Due: ${row[6]} | Status: {row[7]}")
    
    conn.close()
    print('\n✅ Contact information updated successfully!')

if __name__ == '__main__':
    update_contact_info()