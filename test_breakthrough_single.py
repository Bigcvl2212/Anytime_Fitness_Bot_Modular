#!/usr/bin/env python3
"""Test breakthrough method directly with known member ID"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI

def test_breakthrough_with_known_member():
    print("🧪 Testing breakthrough method with known member ID...")
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    # Use Grace's ID from our previous successful tests
    member_id = "185777276"  # Grace Sphatt
    print(f"🔍 Testing with member ID: {member_id}")
    
    result = api.get_member_training_packages_breakthrough(member_id)
    print(f"📊 Result: {result}")
    
    if result.get('success'):
        packages = result.get('packages', [])
        print(f"✅ Found {len(packages)} packages")
        
        for package in packages:
            agreement_id = package.get('agreement_id')
            package_name = package.get('package_name')
            payment_status = package.get('payment_status')
            amount_owed = package.get('amount_owed', 0)
            biweekly_amount = package.get('biweekly_amount', 0)
            print(f"  📦 Agreement {agreement_id}: {package_name}")
            print(f"     💰 Amount owed: ${amount_owed:.2f}")
            print(f"     💲 Biweekly: ${biweekly_amount:.2f}")
            print(f"     📊 Status: {payment_status}")
            print()
    else:
        error = result.get('error', 'Unknown error')
        print(f"❌ Failed: {error}")

if __name__ == "__main__":
    test_breakthrough_with_known_member()