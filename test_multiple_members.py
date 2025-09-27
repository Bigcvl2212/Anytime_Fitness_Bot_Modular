#!/usr/bin/env python3
"""Test breakthrough method with all known member IDs to find past due clients"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI

def test_multiple_members():
    print("🧪 Testing breakthrough method with multiple member IDs...")
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    # Test with multiple known member IDs
    test_members = [
        "185777276",  # Grace Sphatt  
        "185182950",  # Javae Dixon
        "174558923",  # Another test member
        "191215290",  # Member from HAR files
        "191680161",  # Another member
        "189042593",  # Another member
    ]
    
    total_past_due = 0.0
    past_due_count = 0
    
    for member_id in test_members:
        print(f"\n🔍 Testing member ID: {member_id}")
        
        result = api.get_member_training_packages_breakthrough(member_id)
        
        if result.get('success'):
            packages = result.get('packages', [])
            print(f"  ✅ Found {len(packages)} packages")
            
            member_past_due = 0.0
            for package in packages:
                agreement_id = package.get('agreement_id')
                package_name = package.get('package_name')
                payment_status = package.get('payment_status')
                amount_owed = package.get('amount_owed', 0)
                billing_state = package.get('billing_state', 1)
                
                if amount_owed > 0:
                    print(f"  💰 PAST DUE: Agreement {agreement_id} - {package_name}: ${amount_owed:.2f} (billing state: {billing_state})")
                    member_past_due += amount_owed
                else:
                    print(f"  ✅ Current: Agreement {agreement_id} - {package_name}: ${amount_owed:.2f} (billing state: {billing_state})")
            
            if member_past_due > 0:
                total_past_due += member_past_due
                past_due_count += 1
                print(f"  🚨 Member {member_id}: ${member_past_due:.2f} TOTAL PAST DUE")
            else:
                print(f"  ✅ Member {member_id}: Current (no past due amounts)")
        else:
            error = result.get('error', 'Unknown error')
            print(f"  ❌ Failed: {error}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Past Due Clients: {past_due_count}")
    print(f"   Total Past Due: ${total_past_due:.2f}")
    
    if past_due_count == 0:
        print("   ⚠️ No past due clients found - this might explain why dashboard shows 0")

if __name__ == "__main__":
    test_multiple_members()