#!/usr/bin/env python3
"""
Debug billing data extraction from bare list response
Let's examine the actual billing data structure to understand why all amounts are $0.00
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI
import json

def debug_billing_data():
    print("🔍 Debugging billing data extraction from bare list response")
    
    training_api = ClubOSTrainingPackageAPI()
    if not training_api.authenticate():
        print("❌ Authentication failed")
        return
    
    # Test member with known training packages (Grace)
    member_id = 185777276  # Grace
    print(f"\n🎯 Getting raw package agreements for member {member_id}")
    
    agreements_list = training_api.get_package_agreements_list(member_id)
    
    if agreements_list:
        print(f"✅ Found {len(agreements_list)} agreements")
        
        # Examine the first agreement structure in detail
        if agreements_list:
            agreement = agreements_list[0]
            print(f"\n📋 Raw agreement structure:")
            print(json.dumps(agreement, indent=2, default=str))
            
            # Look specifically at billing data
            billing_statuses = agreement.get('billingStatuses', {})
            package_agreement = agreement.get('packageAgreement', {})
            
            # Services are INSIDE the packageAgreement object, not at the top level!
            services = package_agreement.get('packageAgreementMemberServices', [])
            
            print(f"\n💰 Billing analysis:")
            print(f"  billingStatuses: {json.dumps(billing_statuses, indent=4, default=str)}")
            print(f"  packageAgreementMemberServices: {json.dumps(services, indent=4, default=str)}")
            print(f"  packageAgreement: {json.dumps(package_agreement, indent=4, default=str)}")
            
            # Test the current billing extraction logic
            current_billing = billing_statuses.get('current', {})
            billing_state = current_billing.get('billingState', 1)
            
            print(f"\n🔬 Current extraction logic results:")
            print(f"  current_billing: {current_billing}")
            print(f"  billing_state: {billing_state}")
            print(f"  Classification: {'Current' if billing_state == 1 else 'Past Due'}")
            
            # Test biweekly amount calculation
            biweekly_amount = 0.0
            for service in services:
                price_after_discount = float(service.get('priceAfterDiscount', 0))
                units_per_billing = service.get('unitsPerBillingDuration', 1)
                if price_after_discount > 0 and units_per_billing > 0:
                    biweekly_amount += (price_after_discount * units_per_billing)
                print(f"  Service: price=${price_after_discount}, units={units_per_billing}, contribution=${price_after_discount * units_per_billing}")
            
            print(f"  Total biweekly_amount: ${biweekly_amount:.2f}")
            
    else:
        print("❌ No agreements found")

if __name__ == "__main__":
    debug_billing_data()