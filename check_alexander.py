#!/usr/bin/env python3
"""
Check Alexander Ovanin's funding status directly from ClubOS API
"""

import sys
import os
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_alexander_funding():
    """Test Alexander's funding status lookup"""
    
    print("🔍 Testing Alexander Ovanin's funding status...")
    
    # Initialize the ClubOS API
    api = ClubOSTrainingPackageAPI()
    
    # First, let's see if we can find Alexander by searching members
    print("\n=== Step 1: Searching for Alexander by name ===")
    try:
        # Try to search for Alexander in ClubOS
        search_results = api.search_members("Alexander Ovanin")
        if search_results:
            print(f"✅ Found {len(search_results)} members matching 'Alexander Ovanin':")
            for i, member in enumerate(search_results):
                print(f"  {i+1}. {member}")
                
                # If we found a member, try to get their payment status
                member_id = member.get('id') or member.get('member_id')
                if member_id:
                    print(f"\n=== Step 2: Getting payment status for member ID {member_id} ===")
                    payment_status = api.get_member_payment_status(str(member_id))
                    print(f"Payment status: {payment_status}")
                    
                    # Also try to get their agreements/packages
                    print(f"\n=== Step 3: Getting agreements for member ID {member_id} ===")
                    agreements = api.get_member_agreements(str(member_id))
                    if agreements:
                        print(f"Agreements found: {len(agreements)}")
                        for j, agreement in enumerate(agreements):
                            print(f"  Agreement {j+1}: {agreement}")
                    else:
                        print("No agreements found")
        else:
            print("❌ No members found matching 'Alexander Ovanin'")
            
            # Try alternative search terms
            print("\n=== Trying alternative search terms ===")
            for search_term in ["Alexander", "Ovanin", "alex"]:
                print(f"\nSearching for '{search_term}'...")
                results = api.search_members(search_term)
                if results:
                    print(f"Found {len(results)} results for '{search_term}'")
                    for i, member in enumerate(results[:3]):  # Show first 3 results
                        print(f"  {i+1}. {member}")
                else:
                    print(f"No results for '{search_term}'")
                    
    except Exception as e:
        print(f"❌ Error searching for Alexander: {e}")
        logger.exception("Full error details:")
    
    print("\n=== Step 4: Testing the funding lookup function directly ===")
    try:
        # Import the training package cache to test the lookup function
        from clean_dashboard import training_package_cache
        
        # Test the lookup function that the dashboard uses
        funding_data = training_package_cache.lookup_participant_funding("Alexander Ovanin")
        
        if funding_data:
            print("✅ Funding data found:")
            for key, value in funding_data.items():
                print(f"  {key}: {value}")
        else:
            print("❌ No funding data returned from lookup_participant_funding")
            
    except Exception as e:
        print(f"❌ Error testing funding lookup: {e}")
        logger.exception("Full error details:")

if __name__ == "__main__":
    test_alexander_funding()
