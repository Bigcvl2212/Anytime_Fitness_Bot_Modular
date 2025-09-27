#!/usr/bin/env python3
"""
Test the BREAKTHROUGH method with the exact working setup from HAR
"""

import sys
import logging
from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_breakthrough_with_har_data():
    """Test BREAKTHROUGH method with exact HAR context - member 191215290, agreement 1672118"""
    api = ClubOSTrainingPackageAPI()
    
    # Authenticate
    if not api.authenticate():
        logger.error("❌ Authentication failed")
        return
    
    logger.info("✅ Authentication successful")
    
    # Use the exact member ID from HAR where the request worked
    test_member_id = "191215290"  # This is the delegatedUserId from your HAR cookies
    test_agreement_id = "1672118"  # This is the agreement ID that worked
    
    logger.info(f"🎯 Testing BREAKTHROUGH method with HAR context:")
    logger.info(f"   Member ID: {test_member_id}")
    logger.info(f"   Agreement ID: {test_agreement_id}")
    
    # Step 1: Delegate to this member (like in HAR)
    logger.info("🔑 Step 1: Delegating to member context...")
    delegation_success = api.delegate_to_member(test_member_id)
    logger.info(f"🔑 Delegation result: {'✅ Success' if delegation_success else '❌ Failed'}")
    
    if not delegation_success:
        logger.error("❌ Delegation failed - cannot proceed")
        return
    
    # Step 2: Get package agreements list (should work after delegation)
    logger.info("📋 Step 2: Getting package agreements list...")
    agreements_list = api.get_package_agreements_list(test_member_id)
    logger.info(f"📋 Found {len(agreements_list)} agreements: {[a.get('id') for a in agreements_list]}")
    
    # Step 3: Test V2 endpoint with delegation context
    logger.info(f"🔍 Step 3: Testing V2 endpoint for agreement {test_agreement_id} with delegation context...")
    v2_result = api.get_package_agreement_details(test_agreement_id)
    
    if v2_result.get('success'):
        logger.info("✅ V2 endpoint SUCCESS with delegation!")
        
        data = v2_result.get('data', {})
        include_data = data.get('include', {})
        
        # Analyze invoice data like your HAR example
        invoices = include_data.get('invoices', [])
        scheduled_payments = include_data.get('scheduledPayments', [])
        
        logger.info(f"📊 Retrieved data:")
        logger.info(f"  • {len(invoices)} invoices")
        logger.info(f"  • {len(scheduled_payments)} scheduled payments")
        
        # Show actual invoice data like your example
        if invoices:
            logger.info("📋 Invoice Details:")
            for i, invoice in enumerate(invoices, 1):
                invoice_id = invoice.get('id')
                billing_date = invoice.get('billingDate')
                invoice_status = invoice.get('invoiceStatus')
                remaining_total = invoice.get('remainingTotal', 0)
                total = invoice.get('total', 0)
                
                status_text = {1: "Paid", 2: "Pending", 5: "Past Due"}.get(invoice_status, f"Status {invoice_status}")
                logger.info(f"  Invoice {i}: ID={invoice_id}, Date={billing_date}, Status={status_text}, Remaining=${remaining_total}, Total=${total}")
    
    else:
        logger.error(f"❌ V2 endpoint FAILED even with delegation: {v2_result}")
    
    # Step 4: Test the full BREAKTHROUGH method
    logger.info("🎯 Step 4: Testing full BREAKTHROUGH method...")
    breakthrough_result = api.get_member_training_packages_breakthrough(test_member_id)
    
    if breakthrough_result.get('success'):
        packages = breakthrough_result.get('packages', [])
        logger.info(f"🎯 BREAKTHROUGH SUCCESS: Found {len(packages)} training packages")
        
        for i, package in enumerate(packages, 1):
            logger.info(f"Package {i}: {package.get('package_name', 'Unknown')} - Status: {package.get('payment_status', 'Unknown')}")
    else:
        logger.error(f"❌ BREAKTHROUGH FAILED: {breakthrough_result}")

if __name__ == "__main__":
    test_breakthrough_with_har_data()