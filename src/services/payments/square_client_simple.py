#!/usr/bin/env python3
"""
Square Client for Invoice Creation
Connects to the real Square API for invoice creation
"""

import os
import logging
from typing import Dict, Any, Optional
from square.client import Square as SquareClient
from square.environment import SquareEnvironment
import uuid
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Square API configuration
SQUARE_ENVIRONMENT = os.environ.get('SQUARE_ENVIRONMENT', 'production')
SQUARE_SANDBOX_ACCESS_TOKEN = os.environ.get('SQUARE_SANDBOX_ACCESS_TOKEN', 'EAAAEDUxRW0xIwq96S-8ILBKLiKBrqMWojQV1fVRU3XxPQoMwMAmMBhfCow-INm4')
SQUARE_PRODUCTION_ACCESS_TOKEN = os.environ.get('SQUARE_PRODUCTION_ACCESS_TOKEN', 'EAAAET8UzgMjjrZ_3sE8bYYJ4bqY5JqkrJz7tjYvvEgxHG5QQ-uZeCnJ9mOxoeuU')
SQUARE_LOCATION_ID = os.environ.get('SQUARE_LOCATION_ID', 'L2BNRSAVD9YGF')

def get_square_client():
    """Get configured Square client instance."""
    try:
        access_token = SQUARE_SANDBOX_ACCESS_TOKEN if SQUARE_ENVIRONMENT == 'sandbox' else SQUARE_PRODUCTION_ACCESS_TOKEN
        
        if not access_token:
            logger.error("❌ Missing Square access token")
            return None
            
        environment = SquareEnvironment.SANDBOX if SQUARE_ENVIRONMENT == 'sandbox' else SquareEnvironment.PRODUCTION
        
        # Log environment information
        env_name = "SANDBOX" if SQUARE_ENVIRONMENT == 'sandbox' else "PRODUCTION"
        logger.info(f"🔑 Initializing Square client in {env_name} mode with location ID: {SQUARE_LOCATION_ID}")
        
        return SquareClient(
            token=access_token,
            environment=environment
        )
    except Exception as e:
        logger.error(f"❌ Failed to create Square client: {e}")
        return None

def create_square_invoice(member_name: str, amount: float, description: str = "Overdue Payment") -> Dict[str, Any]:
    """
    Create a Square invoice for a member
    
    Args:
        member_name: Name of the member
        amount: Amount due
        description: Description of the invoice
        
    Returns:
        Dict with invoice details or error information
    """
    try:
        logger.info(f"📄 Creating Square invoice for {member_name}: ${amount} - {description}")
        
        # Initialize Square client
        client = get_square_client()
        if not client:
            return {
                'success': False,
                'error': 'Failed to initialize Square client'
            }
        
        # Get location ID
        location_id = SQUARE_LOCATION_ID
        
        # Create a unique invoice number
        invoice_number = f"AF-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
        
        # Prepare invoice data
        invoice_data = {
            "invoice": {
                "location_id": location_id,
                "title": "Anytime Fitness Payment",
                "description": description,
                "primary_recipient": {
                    "customer_id": None,
                    "given_name": member_name,
                    "family_name": "",
                    "email_address": None
                },
                "payment_requests": [
                    {
                        "request_type": "BALANCE",
                        "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                        "fixed_amount_requested_money": {
                            "amount": int(amount * 100),  # Convert to cents
                            "currency": "USD"
                        },
                        "automatic_payment_source": "NONE",
                        "reminders": [
                            {
                                "relative_scheduled_days": -1,
                                "message": f"Your Anytime Fitness payment of ${amount:.2f} is due tomorrow"
                            },
                            {
                                "relative_scheduled_days": 1,
                                "message": f"Your Anytime Fitness payment of ${amount:.2f} is now overdue"
                            }
                        ]
                    }
                ],
                "delivery_method": "EMAIL",
                "invoice_number": invoice_number,
                "accepted_payment_methods": {
                    "card": True,
                    "square_gift_card": True,
                    "bank_account": True,
                    "buy_now_pay_later": True,
                    "cash_app_pay": True
                },
                "sale_or_service_date": datetime.now().strftime("%Y-%m-%d"),
                "store_payment_method_enabled": True
            }
        }
        
        try:
            # Create the invoice
            invoices_api = client.invoices
            result = invoices_api.create(
                invoice=invoice_data["invoice"]
            )
            
            if not result.is_success():
                logger.error(f"❌ Failed to create invoice: {result.errors}")
                return {
                    'success': False,
                    'error': str(result.errors)
                }
            
            invoice = result.body.get('invoice', {})
            invoice_id = invoice.get('id')
            logger.info(f"✅ Created invoice {invoice_id} for {member_name}")
            
            # Publish the invoice to make it active
            publish_result = invoices_api.publish(
                invoice_id=invoice_id,
                version=0,
                idempotency_key=str(uuid.uuid4())
            )
            
            if not publish_result.is_success():
                logger.error(f"❌ Failed to publish invoice: {publish_result.errors}")
                return {
                    'success': False,
                    'error': str(publish_result.errors)
                }
            
            published_invoice = publish_result.body.get('invoice', {})
            invoice_url = published_invoice.get('public_url', '')
            logger.info(f"✅ Published invoice with URL: {invoice_url}")
            
            return {
                'success': True,
                'invoice_id': invoice_id,
                'public_url': invoice_url,
                'status': 'published',
                'message': f"Invoice created for {member_name}: ${amount}",
                'environment': SQUARE_ENVIRONMENT.upper()
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating Square invoice: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to create invoice for {member_name}"
            }
    except Exception as e:
        logger.error(f"❌ Error creating Square invoice: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to create invoice for {member_name}"
        }

def check_invoice_status(invoice_id: str) -> Dict[str, Any]:
    """
    Check the status of a previously created invoice
    
    Args:
        invoice_id: The ID of the invoice to check
        
    Returns:
        Dict with invoice status details
    """
    try:
        logger.info(f"🔍 Checking status of invoice {invoice_id}")
        
        # Initialize Square client
        client = get_square_client()
        if not client:
            return {
                'success': False,
                'error': 'Failed to initialize Square client'
            }
        
        # Get the invoice
        result = client.invoices.get(invoice_id=invoice_id)
        
        if not result.is_success():
            logger.error(f"❌ Failed to get invoice status: {result.errors}")
            return {
                'success': False,
                'error': str(result.errors)
            }
        
        invoice = result.body.get('invoice', {})
        status = invoice.get('status', 'unknown')
        public_url = invoice.get('public_url', '')
        payment_requests = invoice.get('payment_requests', [])
        
        total_paid = 0
        for req in payment_requests:
            paid = req.get('computed_amount_paid_money', {}).get('amount', 0) or 0
            total_paid += paid
            
        total_paid = total_paid / 100.0  # Convert from cents
        
        logger.info(f"✅ Invoice {invoice_id} status: {status}, paid: ${total_paid:.2f}")
        
        return {
            'success': True,
            'invoice_id': invoice_id,
            'status': status,
            'public_url': public_url,
            'total_paid': total_paid,
            'environment': SQUARE_ENVIRONMENT.upper()
        }
        
    except Exception as e:
        logger.error(f"❌ Error checking invoice status: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to check status for invoice {invoice_id}"
        }
