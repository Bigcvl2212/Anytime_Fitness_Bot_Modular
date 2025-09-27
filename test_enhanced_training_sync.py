#!/usr/bin/env python3
"""
Test Enhanced Training Client Sync

This script tests the enhanced ClubOS integration that captures paid invoice data
for monthly revenue analysis.
"""

import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.clubos_integration import ClubOSIntegration
from src.services.database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_enhanced_training_sync():
    """Test the enhanced training client sync with paid invoice data"""
    print("\n" + "="*80)
    print("🧪 TESTING ENHANCED TRAINING CLIENT SYNC")
    print("="*80)
    
    try:
        # Initialize ClubOS integration
        print("\n1️⃣ Initializing ClubOS integration...")
        clubos = ClubOSIntegration()
        
        if not clubos.authenticate():
            print("❌ ClubOS authentication failed")
            return False
        
        print("✅ ClubOS authenticated successfully")
        
        # Get training clients with enhanced invoice data
        print("\n2️⃣ Fetching training clients with enhanced invoice data...")
        training_clients = clubos.get_training_clients()
        
        if not training_clients:
            print("❌ No training clients found")
            return False
        
        print(f"✅ Found {len(training_clients)} training clients")
        
        # Analyze the enhanced data structure
        print("\n3️⃣ Analyzing enhanced data structure...")
        clients_with_paid_invoices = 0
        total_paid_invoices = 0
        total_paid_amount = 0.0
        
        for client in training_clients[:5]:  # Analyze first 5 clients
            client_name = client.get('member_name', 'Unknown')
            package_details = client.get('package_details', [])
            
            print(f"\n👤 {client_name}:")
            
            if isinstance(package_details, list):
                for package in package_details:
                    if isinstance(package, dict):
                        billing_status = package.get('billing_status', {})
                        paid_invoices = billing_status.get('paid', [])
                        
                        if paid_invoices:
                            clients_with_paid_invoices += 1
                            total_paid_invoices += len(paid_invoices)
                            
                            print(f"   📦 {package.get('package_name', 'Unknown Package')}")
                            print(f"   💰 {len(paid_invoices)} paid invoices found!")
                            
                            for payment in paid_invoices[:3]:  # Show first 3 payments
                                amount = payment.get('amount', 0)
                                payment_month = payment.get('payment_month', 'Unknown')
                                paid_date = payment.get('paid_date', 'Unknown')
                                
                                total_paid_amount += float(amount)
                                print(f"       ${amount} paid in {payment_month} (date: {paid_date})")
                        else:
                            print(f"   📦 {package.get('package_name', 'Unknown Package')}: No paid invoices")
        
        print(f"\n📊 ENHANCED DATA ANALYSIS RESULTS:")
        print(f"   Clients with paid invoices: {clients_with_paid_invoices}")
        print(f"   Total paid invoices found: {total_paid_invoices}")
        print(f"   Total paid amount: ${total_paid_amount:,.2f}")
        
        if total_paid_invoices > 0:
            print(f"   ✅ SUCCESS: Enhanced invoice data capture is working!")
            
            # Save to database
            print(f"\n4️⃣ Saving enhanced data to database...")
            db_manager = DatabaseManager()
            success = db_manager.save_training_clients_to_db(training_clients)
            
            if success:
                print(f"   ✅ Successfully saved {len(training_clients)} training clients with enhanced data")
                return True
            else:
                print(f"   ❌ Failed to save training clients to database")
                return False
        else:
            print(f"   ❌ No paid invoice data found - enhancement may not be working")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 ENHANCED TRAINING CLIENT SYNC TEST")
    print("=" * 80)
    
    success = test_enhanced_training_sync()
    
    if success:
        print(f"\n✅ TEST PASSED")
        print(f"   Enhanced training client sync is working correctly!")
        print(f"   You can now run monthly_training_revenue_analysis.py to see revenue data.")
    else:
        print(f"\n❌ TEST FAILED")
        print(f"   The enhanced invoice data capture needs debugging.")

if __name__ == "__main__":
    main()