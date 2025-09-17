#!/usr/bin/env python3

import sqlite3
import json
from datetime import datetime

# Test the collections API logic with local SQLite database
def test_collections_data():
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    # Get past due members
    cursor.execute("""
        SELECT 
            full_name as name,
            email,
            phone,
            mobile_phone,
            amount_past_due as past_due_amount,
            status,
            join_date,
            'member' as type,
            NULL as agreement_id,
            NULL as agreement_type
        FROM members 
        WHERE amount_past_due > 0
        ORDER BY amount_past_due DESC
    """)
    
    past_due_members = cursor.fetchall()
    
    # Get past due training clients with agreement data
    cursor.execute("""
        SELECT 
            member_name as name,
            email,
            phone,
            past_due_amount,
            payment_status as status,
            last_updated,
            'training_client' as type,
            package_details,
            active_packages
        FROM training_clients 
        WHERE past_due_amount > 0
        ORDER BY past_due_amount DESC
    """)
    
    past_due_training = cursor.fetchall()
    
    # Process training clients to extract agreement info
    processed_training = []
    for client in past_due_training:
        client_dict = {
            'name': client[0], 'email': client[1], 'phone': client[2],
            'past_due_amount': client[3], 'status': client[4], 'last_updated': client[5],
            'type': client[6], 'package_details': client[7], 'active_packages': client[8]
        }
        
        # Extract agreement info from package_details
        agreement_id = None
        agreement_type = None
        if client_dict.get('package_details'):
            try:
                details = json.loads(client_dict['package_details'])
                if details and len(details) > 0:
                    agreement_id = details[0].get('agreement_id')
                    agreement_type = details[0].get('package_name', 'Training Package')
            except:
                pass
        
        client_dict['agreement_id'] = agreement_id
        client_dict['agreement_type'] = agreement_type
        processed_training.append(client_dict)
    
    # Combine all past due data
    all_past_due = []
    
    # Add members
    for member in past_due_members:
        member_dict = {
            'name': member[0], 'email': member[1], 'phone': member[2],
            'mobile_phone': member[3], 'past_due_amount': member[4], 'status': member[5],
            'join_date': member[6], 'type': member[7], 'agreement_id': member[8],
            'agreement_type': member[9]
        }
        all_past_due.append(member_dict)
    
    # Add training clients
    all_past_due.extend(processed_training)
    
    print(f"Found {len(all_past_due)} past due accounts:")
    print(f"  - {len(past_due_members)} members")
    print(f"  - {len(processed_training)} training clients")
    
    print("\nTop 5 by amount:")
    for i, account in enumerate(sorted(all_past_due, key=lambda x: x['past_due_amount'], reverse=True)[:5]):
        print(f"  {i+1}. {account['name']}: ${account['past_due_amount']:.2f} ({account['type']})")
        if account['agreement_id']:
            print(f"      Agreement: {account['agreement_id']} - {account['agreement_type']}")
    
    conn.close()
    return all_past_due

if __name__ == "__main__":
    test_collections_data()
