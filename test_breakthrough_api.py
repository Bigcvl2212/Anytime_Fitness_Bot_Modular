#!/usr/bin/env python3
"""
Test script for the new BREAKTHROUGH API methods
Tests the new ClubOS package agreement endpoints
"""

import sys
import os

# Add the src directory to Python path for imports
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services.api.clubos_training_api import ClubOSTrainingPackageAPI
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_breakthrough_api():
    """Test the new BREAKTHROUGH API methods"""
    
    print("🎯 Testing BREAKTHROUGH API Methods")
    print("=" * 50)
    
    # Initialize API
    api = ClubOSTrainingPackageAPI()
    
    # Authenticate
    print("🔐 Authenticating...")
    if not api.authenticate():
        print("❌ Authentication failed!")
        return False
    
    print("✅ Authentication successful!")
    
    # Test member IDs from previous debugging
    test_member_ids = [
        '185182950',  # Javae Dixon
        '185777276',  # Grace Sphatt
        '191680161'   # Another test member
    ]
    
    for member_id in test_member_ids:
        print(f"\n🧪 Testing member ID: {member_id}")
        print("-" * 30)
        
        try:
            # Test the breakthrough method
            result = api.get_member_training_packages_breakthrough(member_id)
            
            if result.get('success'):
                packages = result.get('packages', [])
                total_agreements = result.get('total_agreements', 0)
                processed_agreements = result.get('processed_agreements', 0)
                
                print(f"✅ BREAKTHROUGH SUCCESS for member {member_id}")
                print(f"   📋 Total agreements found: {total_agreements}")
                print(f"   ✅ Processed agreements: {processed_agreements}")
                print(f"   📦 Package data retrieved: {len(packages)}")
                
                # Show package details
                for i, package in enumerate(packages, 1):
                    agreement_id = package.get('agreement_id')
                    list_data = package.get('list_data', {})
                    detail_data = package.get('detail_data', {})
                    
                    package_name = (
                        detail_data.get('name') or 
                        list_data.get('name') or 
                        f"Package {agreement_id}"
                    )
                    
                    print(f"   {i}. Agreement {agreement_id}: {package_name}")
                    
                    # Check for invoice data
                    include_data = detail_data.get('include', {})
                    invoices = include_data.get('invoices', [])
                    if invoices:
                        total_past_due = 0.0
                        for invoice in invoices:
                            if invoice.get('invoiceStatus') in [4, 5]:  # Past due statuses
                                total_past_due += float(invoice.get('total', 0))
                        
                        print(f"      💰 Past due amount: ${total_past_due:.2f}")
                        print(f"      📄 Total invoices: {len(invoices)}")
                    else:
                        print(f"      ℹ️ No invoice data")
                
                if packages:
                    print(f"🎉 BREAKTHROUGH method working successfully!")
                else:
                    print(f"ℹ️ No packages found for member {member_id}")
                    
            else:
                error = result.get('error', 'Unknown error')
                print(f"❌ BREAKTHROUGH failed for member {member_id}: {error}")
                
        except Exception as e:
            print(f"💥 Exception testing member {member_id}: {e}")
    
    print(f"\n🏁 Test complete!")
    return True

if __name__ == "__main__":
    test_breakthrough_api()