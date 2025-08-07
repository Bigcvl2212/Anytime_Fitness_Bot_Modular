#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from clubos_training_api import ClubOSTrainingPackageAPI

def test_dennis_csv_member_id():
    """Test Dennis's CSV member_id as delegate ID"""
    print(f"🔍 Testing Dennis Rost's CSV member_id as delegate ID...")
    print("=" * 60)
    
    # Initialize API
    api = ClubOSTrainingPackageAPI()
    
    print("🔐 Authenticating with ClubOS...")
    success = api.authenticate()
    if not success:
        print("❌ Authentication failed!")
        return False
    print("   ✅ Authentication successful!")
    
    # Dennis's CSV member_id from the latest CSV file
    csv_member_id = 65828815
    
    print(f"🎯 Testing Dennis's CSV member_id as delegate ID: {csv_member_id}")
    
    try:
        # Step 1: Try delegation
        delegation_response = api.session.get(
            f"{api.base_url}/action/Delegate/{csv_member_id}/url=false",
            headers=api.headers
        )
        print(f"Delegation endpoint status: {delegation_response.status_code}")
        
        if delegation_response.status_code == 200:
            # Step 2: Get package agreements
            packages_response = api.session.get(
                f"{api.base_url}/api/agreements/package_agreements/list",
                headers=api.headers
            )
            print(f"Package agreements status: {packages_response.status_code}")
            
            if packages_response.status_code == 200:
                packages_data = packages_response.json()
                
                if 'agreements' in packages_data and len(packages_data['agreements']) > 0:
                    print(f"✅ Found {len(packages_data['agreements'])} agreements for CSV member_id {csv_member_id}")
                    for i, agreement in enumerate(packages_data['agreements'], 1):
                        package_agreement = agreement.get('packageAgreement', {})
                        name = package_agreement.get('name', 'No name')
                        member_id = package_agreement.get('memberId', 'No member ID')
                        print(f"📦 Agreement {i}: {name} (Member ID: {member_id})")
                else:
                    print(f"❌ No agreements found for CSV member_id {csv_member_id}")
            else:
                print(f"❌ Failed to get package agreements: {packages_response.status_code}")
        else:
            print(f"❌ Delegation failed: {delegation_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing CSV member_id: {str(e)}")
    
    print("=" * 60)
    print("🏁 Test complete!")

if __name__ == "__main__":
    test_dennis_csv_member_id()
