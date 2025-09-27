#!/usr/bin/env python3
"""
Test the FIXED breakthrough method that extracts billing data from bare list response
No more V2 dependency!
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI
from src.services.authentication.unified_auth_service import UnifiedAuthService

def test_fixed_breakthrough():
    print("🧪 Testing FIXED breakthrough method (no V2 dependency)")
    
    auth_service = UnifiedAuthService()
    training_api = ClubOSTrainingPackageAPI()
    
    # Test member with known training packages
    member_id = 162720032  # Grace
    print(f"\n🎯 Testing fixed method for member {member_id}")
    
    result = training_api.get_member_training_packages_breakthrough(member_id)
    
    if result.get('success'):
        packages = result.get('data', [])
        print(f"✅ SUCCESS: Found {len(packages)} training packages")
        
        for i, pkg in enumerate(packages, 1):
            print(f"\n📦 Package {i}:")
            print(f"   Agreement ID: {pkg.get('agreement_id')}")
            print(f"   Package Name: {pkg.get('package_name')}")
            print(f"   Trainer: {pkg.get('trainer_name')}")
            print(f"   Payment Status: {pkg.get('payment_status')}")
            print(f"   Past Due Amount: ${pkg.get('amount_owed', 0):.2f}")
            print(f"   Biweekly Amount: ${pkg.get('biweekly_amount', 0):.2f}")
            print(f"   Billing State: {pkg.get('billing_state')}")
            print(f"   Data Source: {pkg.get('data_source')}")
            print(f"   Has Billing Data: {pkg.get('has_billing_data')}")
    else:
        print(f"❌ FAILED: {result.get('error')}")

if __name__ == "__main__":
    test_fixed_breakthrough()