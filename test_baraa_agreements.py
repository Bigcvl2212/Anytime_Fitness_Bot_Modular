#!/usr/bin/env python3
"""
Test script to debug Baraa's training agreements specifically
Member ID: 162720032
Expected: 1 active training package "2025 1X1 Training"
"""

from clubos_training_api import ClubOSTrainingPackageAPI

def test_baraa_agreements():
    """Test agreement discovery for Baraa specifically."""
    api = ClubOSTrainingPackageAPI()
    
    print("🔐 Authenticating to ClubOS...")
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Test with Baraa's member ID
    member_id = "162720032"
    member_name = "Baraa Manasrah"
    
    print(f"\n🏋️ Testing agreement discovery for {member_name} (ID: {member_id})")
    
    # Step 1: Test delegation
    print("🔑 Testing delegation...")
    delegation_success = api.delegate_to_member(member_id)
    print(f"Delegation result: {delegation_success}")
    
    # Step 2: Test agreement discovery
    print("📋 Testing agreement discovery...")
    agreement_ids = api.discover_member_agreement_ids(member_id)
    print(f"Found agreement IDs: {agreement_ids}")
    
    # Step 3: Test full package agreements
    print("🏋️ Testing full package agreements...")
    agreements = api.get_member_package_agreements(member_id)
    print(f"Found {len(agreements)} package agreements:")
    
    for i, agreement in enumerate(agreements, 1):
        print(f"  {i}. Agreement ID: {agreement['agreement_id']}")
        print(f"     Package Name: {agreement['package_name']}")
        print(f"     Trainer: {agreement['trainer_name']}")
        print(f"     Status: {agreement['status']}")
        print(f"     Amount: ${agreement['amount']}")
        print(f"     Sessions Remaining: {agreement['sessions_remaining']}")
        print()
    
    return agreements

if __name__ == "__main__":
    test_baraa_agreements()
