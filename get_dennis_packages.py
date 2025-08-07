#!/usr/bin/env python3
"""
Get Dennis Rost's training packages using his correct ClubOS delegate ID
"""

import sys
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
import json

def get_dennis_training_packages():
    """Get Dennis's training packages using his correct delegate ID from HAR data"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    # Dennis's correct ClubOS delegate user ID from HAR data
    dennis_delegate_id = "189425730"
    
    print(f"🎯 Getting Dennis Rost's training packages using delegate ID: {dennis_delegate_id}")
    
    # First, use the exact delegation endpoint from HAR data
    delegation_response = api.session.get(f"{api.base_url}/action/Delegate/{dennis_delegate_id}/url=false")
    print(f"Delegation endpoint status: {delegation_response.status_code}")
    
    # Now get package agreements
    response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
    print(f"Package agreements status: {response.status_code}")
    
    if response.status_code == 200:
        agreements = response.json()
        print(f"✅ Found {len(agreements)} agreements for Dennis")
        
        if agreements:
            for i, agreement in enumerate(agreements):
                print(f"\n📦 Agreement {i+1}:")
                print(f"   Raw data: {json.dumps(agreement, indent=2)}")
                
                print(f"   ID: {agreement.get('id', 'No ID')}")
                print(f"   Package: {agreement.get('name', 'No name')}")
                print(f"   Status: {agreement.get('agreementStatus', 'No status')}")
                print(f"   Start Date: {agreement.get('startDate', 'No start date')}")
                
                # Get member info
                member_info = agreement.get('member', {})
                print(f"   Member: {member_info.get('name', 'No member name')}")
                print(f"   Member ID: {member_info.get('id', 'No member ID')}")
                
                # Get package services
                services = agreement.get('packageAgreementMemberServices', [])
                print(f"   Services: {len(services)} service(s)")
                for j, service in enumerate(services):
                    print(f"     Service {j+1}: {service.get('name', 'No service name')}")
                    print(f"     Price: ${service.get('unitPrice', 0)}")
                    print(f"     Units per billing: {service.get('unitsPerBillingDuration', 0)}")
                
                # Get billing status
                agreement_id = agreement.get('id')
                if agreement_id:
                    billing_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/{agreement_id}/billing_status")
                    if billing_response.status_code == 200:
                        billing_data = billing_response.json()
                        print(f"   Billing Status: {billing_data.get('status', 'Unknown')}")
                        print(f"   Past Due Amount: ${billing_data.get('pastDueAmount', 0)}")
        else:
            print("❌ No agreements found for Dennis")
    else:
        print(f"❌ Failed to get agreements: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("🔍 Getting Dennis Rost's training packages...")
    print("=" * 60)
    
    get_dennis_training_packages()
    
    print("\n" + "=" * 60)
    print("🏁 Complete!")
