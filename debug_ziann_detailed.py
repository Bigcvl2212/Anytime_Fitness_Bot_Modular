#!/usr/bin/env python3
import sys
sys.path.append('src')
from services.database_manager import DatabaseManager
import json

# Create database manager
db = DatabaseManager()

print('🔍 Detailed analysis for Ziann Crump...')

# Get raw data first
query = """
    SELECT first_name, last_name, clubos_member_id, payment_status, 
           past_due_amount, total_past_due, package_details
    FROM training_clients 
    WHERE first_name LIKE '%ziann%' AND last_name LIKE '%crump%'
"""
results = db.execute_query(query)

if results:
    client = results[0]
    print(f'📊 Raw database data for {client["first_name"]} {client["last_name"]}:')
    print(f'   Past Due Amount: ${client["past_due_amount"]}')
    print(f'   Total Past Due: ${client["total_past_due"]}')
    
    # Parse package details manually
    package_details_str = client['package_details']
    if package_details_str:
        package_details = json.loads(package_details_str)
        print(f'\n📋 Package Details Analysis:')
        if isinstance(package_details, list):
            for i, package in enumerate(package_details):
                print(f'   Package {i+1}:')
                print(f'      Agreement ID: {package.get("agreement_id")}')
                print(f'      Package Name: {package.get("package_name")}')
                print(f'      Amount Owed: ${package.get("amount_owed", 0)}')
                print(f'      Payment Status: {package.get("payment_status")}')
                
                # Check billing status
                billing_status = package.get('billing_status', {})
                if billing_status and 'past' in billing_status:
                    past_items = billing_status['past']
                    total_billing_past = sum(float(item.get('amount', 0)) for item in past_items if isinstance(item, dict))
                    print(f'      Billing Status Past Due: ${total_billing_past}')
                    
        print(f'\n🧮 Expected calculation based on package_details:')
        if isinstance(package_details, list):
            total_from_amount_owed = sum(float(pkg.get('amount_owed', 0)) for pkg in package_details if isinstance(pkg, dict))
            print(f'   Sum of amount_owed fields: ${total_from_amount_owed}')
            
            total_from_billing = 0
            for pkg in package_details:
                if isinstance(pkg, dict) and 'billing_status' in pkg:
                    billing = pkg['billing_status']
                    if 'past' in billing:
                        for item in billing['past']:
                            if isinstance(item, dict):
                                total_from_billing += float(item.get('amount', 0))
            print(f'   Sum from billing_status: ${total_from_billing}')
            
print('\n🖥️  Now testing get_training_clients_with_agreements()...')
clients = db.get_training_clients_with_agreements()
for client in clients:
    if 'ziann' in client.get('first_name', '').lower():
        print(f'   Final amount_owed: ${client.get("amount_owed", 0)}')
        print(f'   Final actual_past_due: ${client.get("actual_past_due", 0)}')
        break