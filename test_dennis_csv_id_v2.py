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
        # Get packages using the API method (should handle delegation internally)
        packages = api.get_member_packages(csv_member_id)
        
        if packages and len(packages) > 0:
            print(f"✅ Found {len(packages)} agreements for CSV member_id {csv_member_id}")
            for i, package in enumerate(packages, 1):
                name = package.get('name', 'No name')
                member_id = package.get('memberId', 'No member ID')
                print(f"📦 Package {i}: {name} (Member ID: {member_id})")
        else:
            print(f"❌ No packages found for CSV member_id {csv_member_id}")
            
    except Exception as e:
        print(f"❌ Error testing CSV member_id: {str(e)}")
    
    print("=" * 60)
    print("🏁 Test complete!")

if __name__ == "__main__":
    test_dennis_csv_member_id()
