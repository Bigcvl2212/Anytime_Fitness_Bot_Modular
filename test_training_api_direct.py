#!/usr/bin/env python3
"""
Direct Training API Test
Test the training API directly to see if data is being fetched correctly
"""

import os
import sys
import logging

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_training_api_direct():
    """Test training API directly"""
    try:
        logger.info("🔍 TESTING TRAINING API DIRECTLY")
        
        # Test the training API
        from clubos_training_api_fixed import ClubOSTrainingPackageAPI
        
        training_api = ClubOSTrainingPackageAPI()
        
        # Get credentials
        try:
            from src.services.authentication.secure_secrets_manager import SecureSecretsManager
            secrets_manager = SecureSecretsManager()
            
            username = secrets_manager.get_secret('clubos-username')
            password = secrets_manager.get_secret('clubos-password')
            
            if username and password:
                training_api.username = username
                training_api.password = password
                logger.info("🔐 Loaded credentials from SecureSecretsManager")
            else:
                logger.error("❌ No credentials found")
                return
                
        except Exception as e:
            logger.error(f"❌ Error loading credentials: {e}")
            return
        
        # Authenticate
        if not training_api.authenticate():
            logger.error("❌ Training API authentication failed")
            return
        
        logger.info("✅ Training API authenticated")
        
        # Get assignees (this should be working based on the logs)
        logger.info("📋 Getting assignees...")
        assignees = training_api.fetch_assignees()
        
        if not assignees:
            logger.error("❌ No assignees found")
            return
        
        logger.info(f"✅ Found {len(assignees)} assignees")
        
        # Test one assignee's agreements and billing
        test_assignee = assignees[0]
        clubos_id = test_assignee.get('tfoUserId') or test_assignee.get('id') or test_assignee.get('memberId')
        full_name = test_assignee.get('name', '').strip()
        
        logger.info(f"🧪 Testing assignee: {full_name} (ID: {clubos_id})")
        
        # Get agreements
        agreements = training_api.get_member_package_agreements(str(clubos_id))
        logger.info(f"📄 Found {len(agreements) if agreements else 0} agreements")
        
        if agreements:
            for i, agreement in enumerate(agreements[:2]):  # Test first 2 agreements
                agreement_id = agreement.get('agreement_id') or agreement.get('id') or agreement.get('agreementId')
                logger.info(f"🔍 Testing agreement {i+1}: {agreement_id}")
                
                # Get billing details
                v2_data = training_api.get_agreement_invoices_and_payments(agreement_id)
                
                if v2_data:
                    detail_data = v2_data.get('data', {})
                    include_data = v2_data.get('include', {})
                    
                    invoices = include_data.get('invoices', [])
                    logger.info(f"💰 Agreement {agreement_id}: {len(invoices)} invoices")
                    
                    # Check invoice statuses
                    past_due_count = 0
                    past_due_amount = 0.0
                    
                    for invoice in invoices:
                        invoice_status = invoice.get('invoiceStatus')
                        invoice_amount = float(invoice.get('total', 0))
                        invoice_id = invoice.get('id', 'unknown')
                        
                        logger.info(f"  📋 Invoice {invoice_id}: ${invoice_amount} (status: {invoice_status})")
                        
                        if invoice_status in [4, 5] and invoice_amount > 0:  # Past due
                            past_due_count += 1
                            past_due_amount += invoice_amount
                    
                    logger.info(f"💰 Agreement {agreement_id}: ${past_due_amount:.2f} past due from {past_due_count} invoices")
                else:
                    logger.warning(f"⚠️ No V2 data for agreement {agreement_id}")
        
        logger.info("🎉 DIRECT API TEST COMPLETE")
        
    except Exception as e:
        logger.error(f"❌ Direct API test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_training_api_direct()