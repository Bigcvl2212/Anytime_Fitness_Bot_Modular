#!/usr/bin/env python3
"""
Debug script to examine the full agreement and invoice data structure
"""

import sys
import os
import json

# Add the src directory to Python path for imports
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services.api.clubos_training_api import ClubOSTrainingPackageAPI
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_agreement_invoice_data():
    """Debug the full agreement and invoice data structure"""
    
    print("🔍 DEBUG: Full Agreement and Invoice Data Analysis")
    print("=" * 60)
    
    # Initialize API
    api = ClubOSTrainingPackageAPI()
    
    # Authenticate
    if not api.authenticate():
        print("❌ Authentication failed!")
        return False
    
    print("✅ Authentication successful!")
    
    # Test member IDs
    test_member_ids = [
        '185777276',  # Grace Sphatt - has 2 agreements
        '185182950'   # Javae Dixon - has 1 agreement
    ]
    
    for member_id in test_member_ids:
        print(f"\n🧪 FULL DEBUG for member ID: {member_id}")
        print("-" * 40)
        
        try:
            # Get the basic agreements list
            agreements_list = api.get_package_agreements_list(member_id)
            print(f"📋 Found {len(agreements_list)} basic agreements")
            
            for i, agreement in enumerate(agreements_list, 1):
                print(f"\n📄 Agreement {i}:")
                print(f"   Raw structure: {json.dumps(agreement, indent=4)[:500]}...")
                
                # Extract agreement ID
                agreement_id = None
                if isinstance(agreement, dict):
                    if 'packageAgreement' in agreement and isinstance(agreement['packageAgreement'], dict):
                        agreement_id = agreement['packageAgreement'].get('id')
                    if not agreement_id:
                        agreement_id = agreement.get('id') or agreement.get('agreementId')
                
                if agreement_id:
                    print(f"   🆔 Agreement ID: {agreement_id}")
                    
                    # Get V2 details
                    details_result = api.get_package_agreement_details(agreement_id)
                    
                    if details_result.get('success'):
                        v2_data = details_result.get('data', {})
                        agreement_data = v2_data.get('data', {})
                        include_data = v2_data.get('include', {})
                        
                        print(f"   📊 Agreement Status: {agreement_data.get('agreementStatus')}")
                        print(f"   📝 Agreement Name: {agreement_data.get('name', 'Unknown')}")
                        print(f"   🎯 Package Name: {agreement_data.get('packageName', 'Unknown')}")
                        
                        # Check invoices
                        invoices = include_data.get('invoices', [])
                        print(f"   💰 Total Invoices: {len(invoices)}")
                        
                        if invoices:
                            total_past_due = 0.0
                            total_paid = 0.0
                            total_pending = 0.0
                            
                            print(f"   📄 Invoice Details:")
                            for j, invoice in enumerate(invoices, 1):
                                invoice_id = invoice.get('id', 'unknown')
                                invoice_status = invoice.get('invoiceStatus')
                                total_amount = float(invoice.get('total', 0))
                                remaining_total = float(invoice.get('remainingTotal', 0))
                                
                                print(f"      {j}. Invoice {invoice_id}:")
                                print(f"         Status: {invoice_status}")
                                print(f"         Total: ${total_amount:.2f}")
                                print(f"         Remaining: ${remaining_total:.2f}")
                                print(f"         Due Date: {invoice.get('dueDate', 'N/A')}")
                                
                                # Calculate totals using working backup logic
                                if invoice_status == 1:  # Paid
                                    total_paid += (total_amount - remaining_total)
                                elif invoice_status == 2:  # Pending payment
                                    total_pending += remaining_total
                                elif invoice_status == 5:  # Delinquent/Past due
                                    total_past_due += remaining_total
                            
                            print(f"   💸 FINANCIAL SUMMARY:")
                            print(f"      Past Due: ${total_past_due:.2f}")
                            print(f"      Pending: ${total_pending:.2f}")
                            print(f"      Paid: ${total_paid:.2f}")
                            
                            payment_status = 'Past Due' if total_past_due > 0 else 'Pending' if total_pending > 0 else 'Current'
                            print(f"      Payment Status: {payment_status}")
                            
                            # Save detailed invoice data to file for analysis
                            invoice_debug_file = f"debug_invoices_{member_id}_{agreement_id}.json"
                            with open(invoice_debug_file, 'w') as f:
                                json.dump({
                                    'member_id': member_id,
                                    'agreement_id': agreement_id,
                                    'agreement_data': agreement_data,
                                    'invoices': invoices,
                                    'financial_summary': {
                                        'total_past_due': total_past_due,
                                        'total_pending': total_pending,
                                        'total_paid': total_paid,
                                        'payment_status': payment_status
                                    }
                                }, f, indent=2)
                            print(f"      💾 Saved detailed data to {invoice_debug_file}")
                        else:
                            print(f"      ℹ️ No invoices found")
                            
                        # Save full V2 data for analysis
                        v2_debug_file = f"debug_v2_data_{member_id}_{agreement_id}.json"
                        with open(v2_debug_file, 'w') as f:
                            json.dump(v2_data, f, indent=2)
                        print(f"   💾 Saved full V2 data to {v2_debug_file}")
                        
                    else:
                        print(f"   ❌ Failed to get V2 details: {details_result.get('error')}")
                else:
                    print(f"   ⚠️ No agreement ID found")
                    
        except Exception as e:
            print(f"💥 Exception debugging member {member_id}: {e}")
    
    print(f"\n🏁 Full debug analysis complete!")
    return True

if __name__ == "__main__":
    debug_agreement_invoice_data()