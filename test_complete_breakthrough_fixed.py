#!/usr/bin/env python3
"""
Test the COMPLETE fixed BREAKTHROUGH method with proper agreement structure handling
"""

import sys
import json
import logging
from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_complete_breakthrough_fixed():
    """Test the complete BREAKTHROUGH method with all fixes applied"""
    api = ClubOSTrainingPackageAPI()
    
    # Authenticate
    if not api.authenticate():
        logger.error("❌ Authentication failed")
        return
    
    logger.info("✅ Authentication successful")
    
    # Use the exact member ID from HAR where everything worked
    test_member_id = "191215290"
    test_agreement_id = "1672118"
    
    logger.info(f"🎯 Testing COMPLETE BREAKTHROUGH with fixes:")
    logger.info(f"   Member ID: {test_member_id}")
    logger.info(f"   Expected Agreement ID: {test_agreement_id}")
    
    # Step 1: Delegate to member (required for V2 endpoint)
    logger.info("🔑 Step 1: Delegating to member...")
    delegation_success = api.delegate_to_member(test_member_id)
    logger.info(f"🔑 Delegation: {'✅ Success' if delegation_success else '❌ Failed'}")
    
    if not delegation_success:
        logger.error("❌ Cannot proceed without delegation")
        return
    
    # Step 2: Test the FIXED get_package_agreements_list method
    logger.info("📋 Step 2: Testing FIXED bare list method...")
    agreements_list = api.get_package_agreements_list(test_member_id)
    
    logger.info(f"📋 Agreements list result: {len(agreements_list) if agreements_list else 0} agreements")
    
    if agreements_list:
        # Check if we can find our expected agreement ID
        found_1672118 = False
        for agreement in agreements_list:
            if isinstance(agreement, dict):
                # Check both the new compatibility id and the nested structure
                agreement_id = agreement.get('id')
                nested_id = None
                if 'packageAgreement' in agreement:
                    nested_id = agreement['packageAgreement'].get('id')
                
                logger.info(f"📋 Agreement: top-level id={agreement_id}, nested id={nested_id}")
                
                if str(agreement_id) == test_agreement_id or str(nested_id) == test_agreement_id:
                    found_1672118 = True
                    logger.info(f"🎯 FOUND target agreement {test_agreement_id}!")
        
        if not found_1672118:
            logger.warning(f"⚠️ Target agreement {test_agreement_id} not found in list")
    
    # Step 3: Test V2 endpoint with delegation context
    logger.info(f"🔍 Step 3: Testing V2 endpoint with delegation context for {test_agreement_id}...")
    v2_result = api.get_package_agreement_details(test_agreement_id)
    
    if v2_result.get('success'):
        logger.info("✅ V2 endpoint SUCCESS with delegation!")
        
        data = v2_result.get('data', {})
        include_data = data.get('include', {})
        
        invoices = include_data.get('invoices', [])
        scheduled_payments = include_data.get('scheduledPayments', [])
        
        logger.info(f"📊 Invoice data retrieved:")
        logger.info(f"  • {len(invoices)} invoices")
        logger.info(f"  • {len(scheduled_payments)} scheduled payments")
        
        # Show invoice details like your HAR example
        if invoices:
            logger.info("📋 Invoice Details:")
            total_remaining = 0
            
            for i, invoice in enumerate(invoices[:3], 1):  # Show first 3
                invoice_id = invoice.get('id')
                billing_date = invoice.get('billingDate')
                invoice_status = invoice.get('invoiceStatus')
                remaining_total = invoice.get('remainingTotal', 0)
                total = invoice.get('total', 0)
                
                status_text = {1: "Paid", 2: "Pending", 5: "Past Due"}.get(invoice_status, f"Status {invoice_status}")
                logger.info(f"  Invoice {i}: ID={invoice_id}, Date={billing_date}, Status={status_text}, Remaining=${remaining_total}, Total=${total}")
                total_remaining += remaining_total
            
            if len(invoices) > 3:
                logger.info(f"  ... and {len(invoices) - 3} more invoices")
            
            logger.info(f"📊 Total remaining across all invoices: ${total_remaining}")
    else:
        logger.error(f"❌ V2 endpoint FAILED: {v2_result}")
    
    # Step 4: Test the COMPLETE BREAKTHROUGH method
    logger.info("🎯 Step 4: Testing COMPLETE BREAKTHROUGH method...")
    breakthrough_result = api.get_member_training_packages_breakthrough(test_member_id)
    
    if breakthrough_result.get('success'):
        packages = breakthrough_result.get('packages', [])
        total_agreements = breakthrough_result.get('total_agreements', 0)
        processed_agreements = breakthrough_result.get('processed_agreements', 0)
        
        logger.info(f"🎯 BREAKTHROUGH SUCCESS!")
        logger.info(f"  • Total agreements found: {total_agreements}")
        logger.info(f"  • Agreements processed: {processed_agreements}")
        logger.info(f"  • Training packages created: {len(packages)}")
        
        for i, package in enumerate(packages, 1):
            package_name = package.get('package_name', 'Unknown')
            payment_status = package.get('payment_status', 'Unknown')
            amount_owed = package.get('amount_owed', 0)
            
            logger.info(f"  Package {i}: {package_name} - Status: {payment_status}, Owed: ${amount_owed}")
            
        # Save detailed results
        with open('breakthrough_complete_results.json', 'w', encoding='utf-8') as f:
            json.dump(breakthrough_result, f, indent=2)
        logger.info("💾 Saved complete results to breakthrough_complete_results.json")
        
    else:
        error = breakthrough_result.get('error', 'Unknown error')
        logger.error(f"❌ BREAKTHROUGH FAILED: {error}")

if __name__ == "__main__":
    test_complete_breakthrough_fixed()