#!/usr/bin/env python3
"""
Test Dennis's CSV member_id as delegate ID using the working approach
"""

import sys
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
import json

def test_dennis_csv_member_id():
    """Test Dennis's CSV member_id as delegate ID"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    # Dennis's CSV member_id from the latest CSV file
    csv_member_id = "65828815"
    
    print(f"🎯 Testing Dennis's CSV member_id as delegate ID: {csv_member_id}")
    
    # Step 1: Try delegation using CSV member_id
    delegation_response = api.session.get(f"{api.base_url}/action/Delegate/{csv_member_id}/url=false")
    print(f"Delegation endpoint status: {delegation_response.status_code}")
    
    if delegation_response.status_code == 200:
        # Step 2: Get package agreements
        response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
        print(f"Package agreements status: {response.status_code}")
        
        if response.status_code == 200:
            agreements = response.json()
            print(f"✅ Found {len(agreements)} agreements for CSV member_id {csv_member_id}")
            
            if agreements:
                for i, agreement in enumerate(agreements):
                    print(f"\n📦 Agreement {i+1}:")
                    
                    # Try to get package agreement data
                    package_agreement = agreement.get('packageAgreement', {})
                    if package_agreement:
                        print(f"   Package: {package_agreement.get('name', 'No name')}")
                        print(f"   Member ID: {package_agreement.get('memberId', 'No member ID')}")
                        print(f"   Status: {package_agreement.get('agreementStatus', 'No status')}")
                        print(f"   Start Date: {package_agreement.get('startDate', 'No start date')}")
                    else:
                        print(f"   Raw data: {json.dumps(agreement, indent=2)}")
            else:
                print("❌ No agreements found for CSV member_id")
        else:
            print(f"❌ Failed to get agreements: {response.status_code}")
    else:
        print(f"❌ Delegation failed: {delegation_response.status_code}")
        print(f"Response text: {delegation_response.text[:200]}...")

if __name__ == "__main__":
    print("🔍 Testing Dennis Rost's CSV member_id as delegate ID...")
    print("=" * 60)
    
    test_dennis_csv_member_id()
    
    print("\n" + "=" * 60)
    print("🏁 Test complete!")
