#!/usr/bin/env python3
"""
Test the fixed agreement ID extraction for training clients
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.clubos_integration import ClubOSIntegration

def test_agreement_extraction():
    """Test if we can properly extract agreement IDs and process them"""
    print("🔍 Testing fixed agreement ID extraction...")
    print("=" * 60)
    
    # Initialize ClubOS integration
    integration = ClubOSIntegration()
    
    # Test with a known training client that has agreements
    test_member_id = "189425730"  # Dennis Rost - we know he has agreements
    
    print(f"🧪 Testing agreement extraction for member: {test_member_id}")
    
    try:
        # Test the fixed _get_working_v2_agreements method
        agreements = integration._get_working_v2_agreements(test_member_id)
        
        print(f"📊 Results:")
        print(f"   Agreements found: {len(agreements)}")
        
        if agreements:
            for i, agreement in enumerate(agreements, 1):
                print(f"   Agreement {i}:")
                print(f"     ID: {agreement.get('agreement_id', 'N/A')}")
                print(f"     Package: {agreement.get('package_name', 'N/A')}")
                print(f"     Status: {agreement.get('payment_status', 'N/A')}")
                print(f"     Amount Owed: ${agreement.get('amount_owed', 0):.2f}")
                print(f"     Unit Price: ${agreement.get('unit_price', 0):.2f}")
        else:
            print("   ❌ No agreements processed")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agreement_extraction()