#!/usr/bin/env python3
"""
Test the fixed V2 endpoint with correct parameter format from HAR
"""

import sys
import logging
from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_fixed_v2_endpoint():
    """Test the V2 endpoint with the CORRECT parameter format from HAR"""
    api = ClubOSTrainingPackageAPI()
    
    # Authenticate
    if not api.authenticate():
        logger.error("❌ Authentication failed")
        return
    
    logger.info("✅ Authentication successful")
    
    # Test with the working agreement ID from your HAR: 1672118
    test_agreement_id = "1672118"
    
    logger.info(f"🧪 Testing V2 endpoint with CORRECT HAR parameters for agreement {test_agreement_id}")
    
    # Test the fixed get_package_agreement_details method
    result = api.get_package_agreement_details(test_agreement_id)
    
    if result.get('success'):
        logger.info("✅ V2 endpoint SUCCESS!")
        
        data = result.get('data', {})
        include_data = data.get('include', {})
        
        # Analyze invoice data
        invoices = include_data.get('invoices', [])
        scheduled_payments = include_data.get('scheduledPayments', [])
        
        logger.info(f"📊 Invoice data retrieved:")
        logger.info(f"  • {len(invoices)} invoices found")
        logger.info(f"  • {len(scheduled_payments)} scheduled payments found")
        
        # Show invoice details like your example
        if invoices:
            logger.info(f"📋 Invoice Details:")
            total_remaining = 0
            paid_count = 0
            pending_count = 0
            
            for i, invoice in enumerate(invoices, 1):
                invoice_id = invoice.get('id')
                billing_date = invoice.get('billingDate')
                invoice_status = invoice.get('invoiceStatus')  # 1=Paid, 2=Pending, etc
                remaining_total = invoice.get('remainingTotal', 0)
                total = invoice.get('total', 0)
                
                status_text = {1: "Paid", 2: "Pending", 5: "Past Due"}.get(invoice_status, f"Status {invoice_status}")
                
                logger.info(f"  Invoice {i}: ID={invoice_id}, Date={billing_date}, Status={status_text}, Remaining=${remaining_total}, Total=${total}")
                
                total_remaining += remaining_total
                if invoice_status == 1:
                    paid_count += 1
                elif invoice_status == 2:
                    pending_count += 1
            
            logger.info(f"📊 Summary: {paid_count} paid, {pending_count} pending, Total remaining: ${total_remaining}")
        
        # Show scheduled payments
        if scheduled_payments:
            logger.info(f"📅 Scheduled Payments:")
            for i, payment in enumerate(scheduled_payments[:5], 1):  # Show first 5
                logger.info(f"  Payment {i}: {payment}")
        
    else:
        logger.error(f"❌ V2 endpoint FAILED: {result}")

if __name__ == "__main__":
    test_fixed_v2_endpoint()