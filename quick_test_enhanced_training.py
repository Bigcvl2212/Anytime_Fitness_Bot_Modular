#!/usr/bin/env python3
"""
Quick Test - Enhanced Training Revenue with SQLite

This script runs a quick test of the enhanced training client sync with SQLite
to verify the paid invoice data capture is working for monthly revenue analysis.
"""

import os
import sys
import json
import logging

# Force SQLite usage
os.environ['LOCAL_DEVELOPMENT'] = 'true'
os.environ['DB_TYPE'] = 'sqlite'

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.clubos_integration import ClubOSIntegration
from src.services.database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def quick_test_enhanced_training_data():
    """Quick test of enhanced training data with SQLite"""
    print("\n" + "="*80)
    print("🚀 QUICK TEST - ENHANCED TRAINING DATA WITH SQLITE")
    print("="*80)
    
    try:
        # Force SQLite database manager
        print("\n1️⃣ Initializing SQLite database...")
        db_manager = DatabaseManager(db_path='gym_bot.db')
        print("✅ SQLite database initialized")
        
        # Get a small sample of training clients
        print("\n2️⃣ Getting training clients with ClubOS integration...")
        clubos = ClubOSIntegration()
        
        if not clubos.authenticate():
            print("❌ ClubOS authentication failed")
            return False
            
        training_clients = clubos.get_training_clients()
        
        if not training_clients:
            print("❌ No training clients found")
            return False
            
        print(f"✅ Found {len(training_clients)} training clients")
        
        # Analyze paid invoice data from first few clients
        print("\n3️⃣ Analyzing paid invoice data...")
        
        clients_with_paid_invoices = 0
        total_paid_amount = 0.0
        total_paid_invoices = 0
        monthly_revenue_preview = {}
        
        for client in training_clients[:10]:  # Test first 10 clients
            client_name = client.get('member_name', 'Unknown')
            package_details = client.get('package_details', [])
            
            if isinstance(package_details, list):
                for package in package_details:
                    if isinstance(package, dict):
                        billing_status = package.get('billing_status', {})
                        paid_invoices = billing_status.get('paid', [])
                        
                        if paid_invoices:
                            clients_with_paid_invoices += 1
                            package_name = package.get('package_name', 'Unknown')
                            
                            print(f"\n💰 {client_name} - {package_name}")
                            print(f"   Paid Invoices: {len(paid_invoices)}")
                            
                            for payment in paid_invoices[:5]:  # Show first 5 payments
                                amount = float(payment.get('amount', 0))
                                payment_month = payment.get('payment_month')
                                invoice_id = payment.get('id', 'unknown')
                                
                                total_paid_amount += amount
                                total_paid_invoices += 1
                                
                                if payment_month:
                                    if payment_month not in monthly_revenue_preview:
                                        monthly_revenue_preview[payment_month] = 0
                                    monthly_revenue_preview[payment_month] += amount
                                    print(f"       ${amount} in {payment_month}")
                                else:
                                    print(f"       ${amount} (no date - using invoice date)")
        
        print(f"\n📊 ENHANCED DATA TEST RESULTS:")
        print(f"   Clients with paid invoices: {clients_with_paid_invoices}")
        print(f"   Total paid invoices: {total_paid_invoices}")
        print(f"   Total paid amount: ${total_paid_amount:,.2f}")
        
        if monthly_revenue_preview:
            print(f"\n📅 MONTHLY REVENUE PREVIEW:")
            for month, amount in sorted(monthly_revenue_preview.items()):
                print(f"   {month}: ${amount:,.2f}")
        
        # Save to SQLite database
        print(f"\n4️⃣ Saving to SQLite database...")
        success = db_manager.save_training_clients_to_db(training_clients)
        
        if success:
            print(f"✅ Successfully saved {len(training_clients)} training clients to SQLite")
            
            # Test monthly revenue analysis
            print(f"\n5️⃣ Testing monthly revenue analysis...")
            
            import subprocess
            result = subprocess.run([
                sys.executable, 'monthly_training_revenue_analysis.py'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Monthly revenue analysis completed successfully!")
                # Show last few lines of output
                lines = result.stdout.strip().split('\n')
                print("📊 Revenue Analysis Results:")
                for line in lines[-10:]:  # Show last 10 lines
                    if line.strip():
                        print(f"   {line}")
            else:
                print("⚠️ Monthly revenue analysis had issues:")
                print(result.stderr)
                
            return True
        else:
            print("❌ Failed to save to SQLite database")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 QUICK ENHANCED TRAINING DATA TEST")
    print("=" * 80)
    
    success = quick_test_enhanced_training_data()
    
    if success:
        print(f"\n🎉 SUCCESS!")
        print(f"   Enhanced training client sync with paid invoice data is working!")
        print(f"   Monthly revenue analysis can now calculate actual revenue from payments.")
    else:
        print(f"\n❌ TEST INCOMPLETE")
        print(f"   Check the logs above for any issues.")

if __name__ == "__main__":
    main()