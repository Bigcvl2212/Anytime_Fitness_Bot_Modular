#!/usr/bin/env python3
"""
Check specific member 52750389 that failed to ban
"""

import sqlite3

def check_member_52750389():
    conn = sqlite3.connect('gym_bot.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    member_id = '52750389'
    
    print(f'🔍 === Checking Member {member_id} ===')
    
    # Check if member exists in database
    cursor.execute('''
    SELECT * FROM members WHERE prospect_id = ?
    ''', (member_id,))
    
    member = cursor.fetchone()
    
    if member:
        print(f'✅ Member found in database:')
        print(f'  ID: {member["prospect_id"]}')
        print(f'  Name: {member["full_name"]}')
        print(f'  Status Message: {member["status_message"]}')
        print(f'  Member Type: {member["member_type"]}')
        print(f'  Agreement Type: {member["agreement_type"]}')
        print(f'  User Type: {member["user_type"]}')
        print(f'  Status: {member["status"]}')
        
        # Check if this member has any invoices (payment issues)
        cursor.execute('''
        SELECT * FROM invoices WHERE member_id = ? ORDER BY due_date DESC LIMIT 5
        ''', (member_id,))
        
        invoices = cursor.fetchall()
        if invoices:
            print(f'\n📄 Recent invoices for member {member_id}:')
            for invoice in invoices:
                print(f'  Invoice {invoice["invoice_id"]}: ${invoice["total_amount"]} due {invoice["due_date"]} - Status: {invoice["status"]}')
        else:
            print(f'\n💰 No invoices found for member {member_id}')
            
        # Check member category  
        if 'Pay Per Visit' in str(member["status_message"] or ''):
            print(f'\n⚠️  This is a PPV member - should not be banned!')
        elif 'Staff' in str(member["status_message"] or ''):
            print(f'\n⚠️  This is a Staff member - might have special restrictions!')
        elif 'Comp' in str(member["status_message"] or ''):
            print(f'\n⚠️  This is a Complimentary member - might have special restrictions!')
        elif member["status_message"] is None or member["status_message"] == '':
            print(f'\n✅ This is a green member (good standing)')
        elif 'Past Due' in str(member["status_message"]):
            print(f'\n📋 This member has past due status - normal candidate for banning')
        else:
            print(f'\n📋 Member status: {member["status_message"]}')
            
    else:
        print(f'❌ Member {member_id} not found in database')
        
    conn.close()

if __name__ == "__main__":
    check_member_52750389()