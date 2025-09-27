#!/usr/bin/env python3
"""
Check Current Revenue Calculations
Debug why training revenue might be showing zero.
"""

import os
import sys
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_revenue():
    """Check current revenue calculations"""
    try:
        from services.database_manager import DatabaseManager
        
        db = DatabaseManager()
        
        print("💰 Current Revenue Calculation:")
        print("=" * 40)
        
        revenue_data = db.get_monthly_revenue_calculation()
        
        print(f"   Member Revenue: ${revenue_data['member_revenue']:.2f}")
        print(f"   Training Revenue: ${revenue_data['training_revenue']:.2f}")
        print(f"   Total Monthly Revenue: ${revenue_data['total_monthly_revenue']:.2f}")
        print(f"   Revenue Members Count: {revenue_data['revenue_members_count']}")
        print(f"   Training Clients Count: {revenue_data['training_clients_count']}")
        
        print("\n🔍 Training Clients Data Analysis:")
        print("=" * 40)
        
        # Check training clients data
        training_clients = db.execute_query("""
            SELECT member_id, member_name, package_details, payment_status, past_due_amount
            FROM training_clients
            WHERE package_details IS NOT NULL AND package_details != ''
            LIMIT 5
        """)
        
        print(f"Total training clients with package_details: {len(training_clients)}")
        
        for i, client in enumerate(training_clients):
            print(f"\nClient {i+1}: {client['member_name']}")
            print(f"  Payment Status: {client['payment_status']}")
            print(f"  Past Due: ${client['past_due_amount'] or 0}")
            
            if client['package_details']:
                try:
                    package_details = json.loads(client['package_details'])
                    print(f"  Package Details Type: {type(package_details)}")
                    
                    if isinstance(package_details, list):
                        print(f"  Number of packages: {len(package_details)}")
                        for j, package in enumerate(package_details):
                            if isinstance(package, dict):
                                # Look for revenue-related fields
                                revenue_fields = {
                                    'recurring_amount': package.get('recurring_amount'),
                                    'monthly_amount': package.get('monthly_amount'), 
                                    'payment_amount': package.get('payment_amount'),
                                    'total_paid': package.get('total_paid'),
                                    'invoice_count': package.get('invoice_count'),
                                    'scheduled_payments_count': package.get('scheduled_payments_count')
                                }
                                print(f"    Package {j+1} revenue fields: {revenue_fields}")
                    else:
                        print(f"  Package Details: {package_details}")
                except json.JSONDecodeError as e:
                    print(f"  JSON Error: {e}")
            else:
                print(f"  No package details")
        
        return revenue_data
        
    except Exception as e:
        print(f"❌ Error checking revenue: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    check_revenue()