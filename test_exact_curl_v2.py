#!/usr/bin/env python3
"""Test the V2 endpoint using EXACT curl format - cookies included."""

import sys
import os
sys.path.append(os.getcwd())

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI
import logging

# Enable debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_exact_curl_v2():
    """Test V2 endpoint with EXACT curl format including cookies."""
    api = ClubOSTrainingPackageAPI()
    
    if not api.authenticate():
        logger.error("❌ Authentication failed")
        return
    
    # Test with agreement ID from your curl (1651819)
    test_agreement_id = "1651819"
    
    print(f"\n{'='*60}")
    print(f"🧪 TESTING V2 ENDPOINT WITH EXACT CURL FORMAT")
    print(f"Agreement ID: {test_agreement_id}")
    print(f"{'='*60}")
    
    result = api.get_package_agreement_details(test_agreement_id)
    
    if result.get('success'):
        print(f"✅ V2 ENDPOINT SUCCESS!")
        print(f"   Agreement ID: {result['agreement_id']}")
        print(f"   Total Invoices: {result['total_invoices']}")
        print(f"   Past Due Amount: ${result['past_due_amount']:.2f}")
        
        invoices = result.get('invoices', [])
        if invoices:
            print(f"\n📄 Invoice Details:")
            for invoice in invoices[:3]:  # Show first 3
                status = invoice.get('status')
                amount = invoice.get('amount', 0)
                invoice_id = invoice.get('id', 'N/A')
                print(f"   Invoice {invoice_id}: Status={status}, Amount=${amount}")
        
        scheduled_payments = result.get('scheduledPayments', [])
        print(f"\n💳 Scheduled Payments: {len(scheduled_payments)}")
        
    else:
        print(f"❌ V2 ENDPOINT FAILED")
        error = result.get('error', 'Unknown error')
        print(f"   Error: {error}")
    
    print(f"{'='*60}")
    return result

if __name__ == "__main__":
    test_exact_curl_v2()