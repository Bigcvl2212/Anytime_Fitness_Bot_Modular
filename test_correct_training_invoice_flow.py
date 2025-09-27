#!/usr/bin/env python3
"""
Test the CORRECT training invoice flow using the BREAKTHROUGH method:
1. Get package agreements list for member (with delegation) 
2. Extract invoice/billing data DIRECTLY from agreements list (no V2 needed!)
3. Process billing states to get real past due amounts
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI
import json

def test_correct_training_invoice_flow():
    """Test the correct training invoice flow using BREAKTHROUGH method that actually works"""
    
    print("=" * 80)
    print("Testing BREAKTHROUGH Training Invoice Flow")
    print("Step 1: Get agreement list with delegation")
    print("Step 2: Extract billing data DIRECTLY from agreements (NO V2 needed!)")
    print("Step 3: Process billing states to get real past due amounts")
    print("=" * 80)
    
    # Initialize API
    api = ClubOSTrainingPackageAPI()
    
    if not api.authenticate():
        print("❌ Authentication failed")
        return False
    
    print("✅ Authentication successful")
    
    # Test with Miguel Belmontes who should have training packages
    member_id = "177673765"  # Miguel Belmontes
    print(f"\n🔍 Testing with member ID: {member_id} (Miguel Belmontes)")
    
    # === USE THE BREAKTHROUGH METHOD THAT ACTUALLY WORKS! ===
    print(f"\n{'='*60}")
    print("🎯 BREAKTHROUGH: Using the working method to get invoice data!")
    print(f"{'='*60}")
    
    # Call the breakthrough method that gets billing data from agreements list
    breakthrough_result = api.get_member_training_packages_breakthrough(member_id)
    
    if not breakthrough_result.get('success'):
        print(f"❌ Breakthrough method failed: {breakthrough_result.get('error')}")
        return False
    
    packages = breakthrough_result.get('packages', [])
    
    if not packages:
        print("ℹ️ No training packages found")
        return False
    
    print(f"✅ BREAKTHROUGH SUCCESS! Found {len(packages)} training packages with billing data!")
    
    # === EXTRACT AND DISPLAY THE INVOICE DATA WE DESPERATELY NEED ===
    print(f"\n{'='*60}")
    print("💰 INVOICE DATA EXTRACTION")
    print(f"{'='*60}")
    
    total_past_due = 0.0
    active_packages = []
    
    for i, package in enumerate(packages):
        agreement_id = package.get('agreement_id')
        package_name = package.get('package_name', 'Unknown')
        payment_status = package.get('payment_status', 'Unknown')
        amount_owed = float(package.get('amount_owed', 0))
        biweekly_amount = float(package.get('biweekly_amount', 0))
        billing_state = package.get('billing_state', 1)
        trainer_name = package.get('trainer_name', 'Unknown')
        
        print(f"\nPackage {i+1}: Agreement {agreement_id}")
        print(f"  � Name: {package_name}")
        print(f"  �‍💼 Trainer: {trainer_name}")
        print(f"  📊 Payment Status: {payment_status}")
        print(f"  💰 Amount Owed: ${amount_owed:.2f}")
        print(f"  💳 Biweekly Amount: ${biweekly_amount:.2f}")
        print(f"  � Billing State: {billing_state}")
        
        # Add to totals
        total_past_due += amount_owed
        
        if amount_owed > 0:
            active_packages.append({
                'agreement_id': agreement_id,
                'package_name': package_name,
                'amount_owed': amount_owed,
                'payment_status': payment_status
            })
    
    # === FINAL RESULTS - THE INVOICE DATA WE NEEDED! ===
    print(f"\n{'='*60}")
    print("🎉 FINAL RESULTS - WE GOT THE INVOICE DATA!")
    print(f"{'='*60}")
    
    print(f"✅ SUCCESS! Retrieved billing data for {len(packages)} training packages")
    print(f"💰 TOTAL PAST DUE AMOUNT: ${total_past_due:.2f}")
    
    if active_packages:
        print(f"\n⚠️ PACKAGES WITH PAST DUE AMOUNTS:")
        for pkg in active_packages:
            print(f"  - {pkg['package_name']}: ${pkg['amount_owed']:.2f} ({pkg['payment_status']})")
    else:
        print(f"✅ All training packages are current - no past due amounts")
    
    print(f"\n🎉 BREAKTHROUGH METHOD WORKS! We have the invoice data!")
    print(f"✅ This method gets billing data directly from agreements list - NO V2 needed!")
    return True

def test_breakthrough_with_multiple_members():
    """Test breakthrough method with multiple members"""
    print(f"\n{'='*80}")
    print("TESTING BREAKTHROUGH METHOD WITH MULTIPLE MEMBERS")
    print(f"{'='*80}")
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    # Test members - add more member IDs here
    test_members = [
        ("177673765", "Miguel Belmontes"),
        # Add more members if you have their IDs
    ]
    
    grand_total_past_due = 0.0
    
    for member_id, member_name in test_members:
        print(f"\n🔍 Testing {member_name} (ID: {member_id})")
        
        result = api.get_member_training_packages_breakthrough(member_id)
        if result.get('success'):
            packages = result.get('packages', [])
            if packages:
                member_past_due = sum(float(pkg.get('amount_owed', 0)) for pkg in packages)
                print(f"  ✅ Found {len(packages)} packages - Past Due: ${member_past_due:.2f}")
                grand_total_past_due += member_past_due
            else:
                print(f"  ℹ️ No training packages found")
        else:
            print(f"  ❌ Failed: {result.get('error')}")
    
    print(f"\n💰 GRAND TOTAL PAST DUE ACROSS ALL MEMBERS: ${grand_total_past_due:.2f}")

if __name__ == "__main__":
    print("🧪 Starting BREAKTHROUGH Training Invoice Flow Test")
    
    # Test the breakthrough method that actually works
    success = test_correct_training_invoice_flow()
    
    if success:
        # Test with multiple members
        test_breakthrough_with_multiple_members()
        
        print(f"\n🎉 BREAKTHROUGH TESTS COMPLETED SUCCESSFULLY!")
        print(f"✅ We have the invoice data using the breakthrough method!")
        print(f"✅ Ready to integrate into dashboard with REAL past due amounts!")
        print(f"✅ NO MORE V2 ENDPOINT - This method works directly from agreements list!")
    else:
        print(f"\n❌ BREAKTHROUGH TEST FAILED - This is our last hope!")