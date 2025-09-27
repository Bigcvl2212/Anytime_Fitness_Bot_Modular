#!/usr/bin/env python3
"""
Training Revenue Breakdown
Show detailed breakdown of how training revenue is calculated.
"""

import os
import sys
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def show_training_revenue_breakdown():
    """Show detailed breakdown of training revenue calculation"""
    try:
        from services.database_manager import DatabaseManager
        
        db = DatabaseManager()
        
        print("💰 Training Revenue Detailed Breakdown:")
        print("=" * 50)
        
        # Get training clients with enhanced data
        clients = db.execute_query("""
            SELECT member_name, package_details, payment_status
            FROM training_clients
            WHERE package_details LIKE '%paid_invoices%'
            ORDER BY member_name
        """)
        
        total_training_revenue = 0.0
        
        for client in clients:
            client_revenue = 0.0
            invoice_count = 0
            
            try:
                package_data = json.loads(client['package_details'])
                if isinstance(package_data, list):
                    for package in package_data:
                        if isinstance(package, dict) and 'paid_invoices' in package:
                            paid_invoices = package['paid_invoices']
                            
                            # Calculate revenue from paid invoices
                            invoice_total = sum(float(inv.get('amount', 0)) for inv in paid_invoices)
                            invoice_count = len(paid_invoices)
                            
                            if invoice_count > 1:
                                # Estimate monthly recurring
                                estimated_monthly = invoice_total / invoice_count
                                client_revenue += estimated_monthly
                            elif invoice_total > 0:
                                # Single payment
                                client_revenue += invoice_total
                
                if client_revenue > 0:
                    print(f"{client['member_name']:<25} | ${client_revenue:>8.2f} | {invoice_count:>3} invoices | {client['payment_status']}")
                    total_training_revenue += client_revenue
                    
            except Exception as e:
                print(f"Error processing {client['member_name']}: {e}")
        
        print("=" * 50)
        print(f"{'TOTAL TRAINING REVENUE':<25} | ${total_training_revenue:>8.2f}")
        print("=" * 50)
        
        # Show overall revenue summary
        revenue_data = db.get_monthly_revenue_calculation()
        print(f"\n📊 Complete Revenue Summary:")
        print(f"   Member Revenue:    ${revenue_data['member_revenue']:>8.2f}")
        print(f"   Training Revenue:  ${revenue_data['training_revenue']:>8.2f}")
        print(f"   ────────────────────────────────")
        print(f"   Total Monthly:     ${revenue_data['total_monthly_revenue']:>8.2f}")
        
        return total_training_revenue
        
    except Exception as e:
        print(f"❌ Error showing training revenue breakdown: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return 0

if __name__ == "__main__":
    show_training_revenue_breakdown()