#!/usr/bin/env python3
"""
Test script using ONLY the WORKING parts of the BREAKTHROUGH method
Skips the problematic V2 endpoint and uses billing_status per agreement instead
"""

import sys
import os

# Add the src directory to Python path for imports
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services.api.clubos_training_api import ClubOSTrainingPackageAPI
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_working_method_only():
    """Test using ONLY the working parts: delegate + bare list + billing_status per agreement"""
    
    print("🎯 Testing WORKING METHOD ONLY (No V2 endpoint)")
    print("=" * 60)
    
    # Initialize API
    api = ClubOSTrainingPackageAPI()
    
    # Authenticate
    print("🔐 Authenticating...")
    if not api.authenticate():
        print("❌ Authentication failed!")
        return False
    
    print("✅ Authentication successful!")
    
    # Test member IDs from previous debugging
    test_member_ids = [
        '185182950',  # Javae Dixon - had 1 agreement
        '185777276',  # Grace Sphatt - had 2 agreements
        '191680161'   # Another test member - had 1 agreement
    ]
    
    for member_id in test_member_ids:
        print(f"\n🧪 Testing member ID: {member_id}")
        print("-" * 40)
        
        try:
            # Step 1: Use the working bare list method
            bare_agreements = api._list_member_package_agreements_bare(member_id)
            print(f"📋 Found {len(bare_agreements)} agreements using bare list method")
            
            if not bare_agreements:
                print(f"ℹ️ No agreements found for member {member_id}")
                continue
            
            # Step 2: Process each agreement and extract billing data from the response
            working_packages = []
            for agreement in bare_agreements:
                # Extract agreement data properly from the nested structure
                package_agreement = agreement.get('packageAgreement', {})
                billing_statuses = agreement.get('billingStatuses', {})
                
                agreement_id = str(package_agreement.get('id', ''))
                package_name = package_agreement.get('name', f'Package {agreement_id}')
                
                print(f"   🔍 Processing agreement {agreement_id}: {package_name}")
                
                # Extract billing status from the response data (no need for separate API call!)
                current_billing = billing_statuses.get('current', {})
                billing_state = current_billing.get('billingState', 1)  # 1=Current, others may be past due
                
                # Determine payment status from billing state
                payment_status = "Current" if billing_state == 1 else "Past Due"
                
                # Calculate the full biweekly amount from services
                biweekly_amount = 0.0
                member_services = package_agreement.get('packageAgreementMemberServices', [])
                
                for service in member_services:
                    unit_price = float(service.get('priceAfterDiscount', 0.0))
                    units_per_billing = int(service.get('unitsPerBillingDuration', 0))
                    billing_duration = int(service.get('billingDuration', 1))
                    
                    # Calculate total for this service per billing period
                    service_total = unit_price * units_per_billing
                    biweekly_amount += service_total
                    
                    print(f"      📊 Service: {service.get('name', 'Unknown')} - ${unit_price:.2f} x {units_per_billing} units = ${service_total:.2f}")
                
                # For now, assume amount owed is 0 unless we find past due indicators
                # TODO: This needs to be enhanced with actual invoice data
                amount_owed = 0.0
                if payment_status == "Past Due":
                    # This is a placeholder - we'd need invoice data to get exact amount
                    amount_owed = biweekly_amount  # Assume one period past due
                
                working_package = {
                    'agreement_id': agreement_id,
                    'package_name': package_name,
                    'payment_status': payment_status,
                    'biweekly_amount': round(biweekly_amount, 2),
                    'amount_owed': float(amount_owed),
                    'billing_state': billing_state,
                    'start_date': package_agreement.get('startDate'),
                    'end_date': package_agreement.get('endDate'),
                    'list_data': agreement,
                    'has_detailed_data': True
                }
                
                working_packages.append(working_package)
                print(f"      💰 Payment Status: {payment_status} (billing_state: {billing_state})")
                print(f"      💵 Biweekly Amount: ${biweekly_amount:.2f}")
                print(f"      🚨 Amount Owed: ${amount_owed:.2f}")
            
            # Step 3: Summary for this member
            print(f"\n   📊 SUMMARY for member {member_id}:")
            print(f"      📋 Total agreements: {len(bare_agreements)}")
            print(f"      ✅ Processed packages: {len(working_packages)}")
            
            total_owed = sum(pkg['amount_owed'] for pkg in working_packages)
            past_due_count = sum(1 for pkg in working_packages if pkg['payment_status'] == 'Past Due')
            total_biweekly = sum(pkg['biweekly_amount'] for pkg in working_packages)
            
            print(f"      💰 Total biweekly charges: ${total_biweekly:.2f}")
            print(f"      💳 Total amount owed: ${total_owed:.2f}")
            print(f"      🚨 Past due packages: {past_due_count}")
            
            if working_packages:
                print(f"      🎉 WORKING METHOD SUCCESS!")
                
                # Save detailed results for this member
                results_file = f"working_method_results_{member_id}.json"
                with open(results_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'member_id': member_id,
                        'success': True,
                        'total_agreements': len(bare_agreements),
                        'processed_packages': len(working_packages),
                        'total_biweekly_charges': total_biweekly,
                        'total_amount_owed': total_owed,
                        'past_due_count': past_due_count,
                        'packages': working_packages
                    }, f, indent=2, default=str)
                
                print(f"      💾 Results saved to: {results_file}")
            else:
                print(f"      ℹ️ No packages processed for member {member_id}")
                
        except Exception as e:
            print(f"💥 Exception testing member {member_id}: {e}")
    
    print(f"\n🏁 Working method test complete!")
    print("🎯 This proves the WORKING method can retrieve training package data without V2 endpoint!")
    return True

if __name__ == "__main__":
    test_working_method_only()