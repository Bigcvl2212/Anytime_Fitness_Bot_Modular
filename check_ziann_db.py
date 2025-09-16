#!/usr/bin/env python3
import sys
sys.path.append('src')
from services.database_manager import DatabaseManager

# Create database manager
db = DatabaseManager()

print('🔍 Checking Ziann Crump in our database...')

# Query for Ziann Crump in training_clients table
query = """
    SELECT first_name, last_name, clubos_member_id, payment_status, 
           past_due_amount, total_past_due, package_details
    FROM training_clients 
    WHERE first_name LIKE '%ziann%' AND last_name LIKE '%crump%'
"""
results = db.execute_query(query)

if results:
    for client in results:
        print(f'✅ Found in database: {client["first_name"]} {client["last_name"]}')
        print(f'   ClubOS Member ID: {client["clubos_member_id"]}')
        print(f'   Payment Status: {client["payment_status"]}')
        print(f'   Past Due Amount: ${client["past_due_amount"]}')
        print(f'   Total Past Due: ${client["total_past_due"]}')
        print(f'   Package Details: {str(client["package_details"])[:200]}...')
else:
    print('❌ No records found for Ziann Crump in database')
    
# Also check what the training clients page would show
print()
print('🖥️  Checking what training clients page shows...')
clients_with_agreements = db.get_training_clients_with_agreements()
for client in clients_with_agreements:
    if 'ziann' in client.get('first_name', '').lower() and 'crump' in client.get('last_name', '').lower():
        print(f'✅ Training clients page shows: {client["first_name"]} {client["last_name"]}')
        print(f'   Amount owed: ${client.get("amount_owed", 0)}')
        print(f'   Payment status: {client.get("payment_status", "Unknown")}')
        print(f'   Package details length: {len(str(client.get("package_details", "")))} chars')
        break
else:
    print('❌ Ziann not found in training clients with agreements')