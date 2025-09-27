#!/usr/bin/env python3
"""
Check if Enhanced Training Revenue Data Exists
Check if we have the enhanced training data with paid invoices.
"""

import os
import sys
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_enhanced_training_data():
    """Check for enhanced training data with paid invoices"""
    try:
        from services.database_manager import DatabaseManager
        
        db = DatabaseManager()
        
        print("🔍 Checking Enhanced Training Data:")
        print("=" * 40)
        
        # Check if we have paid_invoices data
        clients = db.execute_query("""
            SELECT member_name, package_details 
            FROM training_clients 
            WHERE package_details LIKE '%paid_invoices%' 
            LIMIT 5
        """)
        
        print(f"Clients with paid_invoices data: {len(clients)}")
        
        if len(clients) > 0:
            print("\n✅ Enhanced training data found!")
            
            for client in clients:
                print(f"\nClient: {client['member_name']}")
                try:
                    package_data = json.loads(client['package_details'])
                    if isinstance(package_data, list) and len(package_data) > 0:
                        pkg = package_data[0]
                        if 'paid_invoices' in pkg:
                            paid_invoices = pkg['paid_invoices']
                            print(f"  Paid invoices count: {len(paid_invoices)}")
                            
                            # Calculate revenue from paid invoices
                            total_revenue = sum(float(inv.get('invoice_amount', 0)) for inv in paid_invoices)
                            print(f"  Total paid amount: ${total_revenue:.2f}")
                            
                            if len(paid_invoices) > 0:
                                print(f"  Sample invoice: {paid_invoices[0]}")
                except Exception as e:
                    print(f"  Error parsing package_details: {e}")
        else:
            print("❌ No enhanced training data with paid_invoices found")
            print("\n🔧 The enhanced training sync needs to be run to capture paid invoice data")
            
            # Check regular training data structure
            all_clients = db.execute_query("""
                SELECT member_name, package_details 
                FROM training_clients 
                WHERE package_details IS NOT NULL 
                LIMIT 3
            """)
            
            print(f"\nRegular training clients: {len(all_clients)}")
            for client in all_clients:
                print(f"Client: {client['member_name']}")
                try:
                    package_data = json.loads(client['package_details'])
                    if isinstance(package_data, list) and len(package_data) > 0:
                        pkg = package_data[0]
                        print(f"  Available fields: {list(pkg.keys())}")
                except Exception as e:
                    print(f"  Error: {e}")
        
        return len(clients) > 0
        
    except Exception as e:
        print(f"❌ Error checking enhanced training data: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    check_enhanced_training_data()