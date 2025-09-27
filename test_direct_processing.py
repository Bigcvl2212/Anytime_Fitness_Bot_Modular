#!/usr/bin/env python3
"""
Test script to process agreement data directly from the list response instead of V2 API calls.
"""

import os
import sys

# Add the src directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from services.api.clubos_training_api import ClubOSTrainingPackageAPI
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def extract_past_due_from_agreement(agreement_data):
    """Extract past due amount from agreement data."""
    try:
        # Look for billing status and invoice information
        billing_statuses = agreement_data.get('billingStatuses', {})
        past_due_amount = 0.0
        
        logger.info(f"🔍 Analyzing agreement: {agreement_data.get('packageAgreement', {}).get('id', 'Unknown')}")
        
        # Check current billing status
        current = billing_statuses.get('current', {})
        billing_state = current.get('billingState', 0)
        logger.info(f"  📊 Current billing state: {billing_state}")
        
        # Check for past due billing statuses
        past = billing_statuses.get('past', [])
        logger.info(f"  📜 Past billing events: {len(past)}")
        
        # Look for package agreement details that might contain amounts
        package_agreement = agreement_data.get('packageAgreement', {})
        member_services = package_agreement.get('packageAgreementMemberServices', [])
        
        for service in member_services:
            unit_price = service.get('unitPrice', 0)
            units_per_billing = service.get('unitsPerBillingDuration', 0)
            logger.info(f"  💰 Service: {service.get('name')} - ${unit_price} x {units_per_billing}")
        
        return past_due_amount
        
    except Exception as e:
        logger.error(f"❌ Error processing agreement: {e}")
        return 0.0

def main():
    print("🧪 Testing Direct Processing of Agreement Data")
    print("=" * 50)
    
    # Initialize API
    api = ClubOSTrainingPackageAPI()
    
    print("🔐 Authenticating...")
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful!")
    
    # Test with a member who has agreements
    test_member_id = "185777276"
    print(f"\n🧪 Testing member ID: {test_member_id}")
    print("-" * 30)
    
    # Get the raw agreement list data
    agreements = api.get_package_agreements_list(test_member_id)
    
    if not agreements:
        print("ℹ️ No agreements found")
        return
    
    print(f"📋 Found {len(agreements)} agreements")
    
    # Process each agreement to extract past due information
    total_past_due = 0.0
    active_packages = []
    
    for i, agreement in enumerate(agreements, 1):
        print(f"\n📦 Processing agreement {i}/{len(agreements)}")
        
        # Extract basic info
        package_agreement = agreement.get('packageAgreement', {})
        agreement_id = package_agreement.get('id', 'Unknown')
        agreement_name = package_agreement.get('name', f'Package {agreement_id}')
        agreement_status = package_agreement.get('agreementStatus', 0)
        
        print(f"  🆔 Agreement ID: {agreement_id}")
        print(f"  📋 Name: {agreement_name}")
        print(f"  📊 Status: {agreement_status}")
        
        # Only process active agreements (status 2 = active)
        if agreement_status == 2:
            print(f"  ✅ Agreement is ACTIVE")
            active_packages.append(agreement_name)
            
            # Extract past due amount
            past_due = extract_past_due_from_agreement(agreement)
            total_past_due += past_due
            print(f"  💰 Past due: ${past_due}")
        else:
            print(f"  ⚠️ Agreement is INACTIVE (status {agreement_status})")
    
    print(f"\n📊 SUMMARY:")
    print(f"  🏷️ Active packages: {len(active_packages)}")
    print(f"  📦 Package names: {active_packages}")
    print(f"  💰 Total past due: ${total_past_due}")
    
    print("\n🏁 Test complete!")

if __name__ == "__main__":
    main()