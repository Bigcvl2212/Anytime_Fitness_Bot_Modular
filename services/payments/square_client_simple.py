"""
Simplified Square Payment Service - Dashboard Beta Integration
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Try to import Square SDK
try:
    from square.client import Square as SquareClient
    from square.environment import SquareEnvironment
    SQUARE_AVAILABLE = True
except ImportError:
    SQUARE_AVAILABLE = False
    logger.warning("Square SDK not available - invoicing functionality will be limited")

# Try to import secrets management
try:
    from config.secrets_local import get_secret
    SECRETS_AVAILABLE = True
except ImportError:
    SECRETS_AVAILABLE = False
    logger.warning("Secrets management not available - using environment variables")

def get_square_credentials():
    """Get Square credentials from secrets or environment"""
    if SECRETS_AVAILABLE:
        try:
            # Production by default, with fallback to sandbox
            environment = os.getenv('SQUARE_ENVIRONMENT', 'production')
            
            if environment == 'production':
                access_token = get_secret("square-production-access-token")
                location_id = get_secret("square-production-location-id")
            else:
                access_token = get_secret("square-sandbox-access-token") 
                location_id = get_secret("square-sandbox-location-id")
                
            return {
                'access_token': access_token,
                'location_id': location_id,
                'environment': environment
            }
        except Exception as e:
            logger.error(f"Failed to get secrets: {e}")
    
    # Fallback to environment variables
    environment = os.getenv('SQUARE_ENVIRONMENT', 'sandbox')
    return {
        'access_token': os.getenv(f'SQUARE_{environment.upper()}_ACCESS_TOKEN'),
        'location_id': os.getenv('SQUARE_LOCATION_ID'),
        'environment': environment
    }

def get_square_client():
    """
    Get configured Square client instance.
    
    Returns:
        SquareClient: Configured Square client or None if failed
    """
    if not SQUARE_AVAILABLE:
        logger.error("Square SDK not available")
        return None
        
    try:
        creds = get_square_credentials()
        access_token = creds['access_token']
        
        if not access_token:
            logger.error("Missing Square access token")
            return None
            
        env = SquareEnvironment.PRODUCTION if creds['environment'] == 'production' else SquareEnvironment.SANDBOX
        return SquareClient(
            token=access_token,
            environment=env
        )
    except Exception as e:
        logger.error(f"Failed to create Square client: {e}")
        return None

def create_square_invoice(member_name: str, member_email: str = None, amount: float = 0.0, description: str = "Training Package Payment") -> Dict[str, Any]:
    """
    Create a Square invoice for a member.
    
    Args:
        member_name (str): Name of the member
        member_email (str): Email address for invoice delivery
        amount (float): Amount owed
        description (str): Description for the invoice
        
    Returns:
        dict: Response with success status, invoice_id, and details
    """
    try:
        logger.info(f"Creating Square invoice for {member_name}, amount: ${amount:.2f}")
        
        # Validate inputs
        if not member_name or amount <= 0:
            return {
                'success': False,
                'error': 'Invalid member name or amount'
            }
        
        # Initialize Square client
        client = get_square_client()
        if not client:
            return {
                'success': False,
                'error': 'Could not initialize Square client'
            }
        
        # Get credentials for location ID
        creds = get_square_credentials()
        location_id = creds['location_id']
        
        if not location_id:
            return {
                'success': False,
                'error': 'Missing Square location ID'
            }
        
        # Prepare invoice data
        invoice_request = {
            "request_method": "EMAIL" if member_email else "SHARE_MANUALLY",
            "request_type": "BALANCE",
            "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "primary_recipient": {
                "name": member_name
            },
            "payment_requests": [
                {
                    "request_method": "EMAIL" if member_email else "SHARE_MANUALLY",
                    "request_type": "BALANCE"
                }
            ],
            "description": description,
            "invoice_number": f"AF-{datetime.now().strftime('%Y%m%d')}-{member_name.replace(' ', '')[:10]}",
            "title": "Anytime Fitness Payment",
            "text": f"Payment for {description}",
            "location_id": location_id
        }
        
        # Add email if provided
        if member_email:
            invoice_request["primary_recipient"]["email_address"] = member_email
        
        # Add order with line items
        order_request = {
            "location_id": location_id,
            "line_items": [
                {
                    "name": description,
                    "quantity": "1",
                    "item_type": "ITEM_VARIATION",
                    "base_price_money": {
                        "amount": int(amount * 100),  # Convert to cents
                        "currency": "USD"
                    }
                }
            ]
        }
        
        # Create the order first
        orders_api = client.orders
        order_result = orders_api.create_order(
            location_id=location_id,
            body={"order": order_request}
        )
        
        if order_result.is_error():
            logger.error(f"Error creating Square order: {order_result.errors}")
            return {
                'success': False,
                'error': f'Order creation failed: {order_result.errors}'
            }
        
        order = order_result.body.get('order', {})
        order_id = order.get('id')
        
        # Add order to invoice request
        invoice_request['order"] = {
            "location_id": location_id,
            "order_id": order_id
        }
        
        # Create the invoice
        invoices_api = client.invoices
        create_result = invoices_api.create_invoice(
            body={"invoice": invoice_request}
        )
        
        if create_result.is_error():
            logger.error(f"Error creating Square invoice: {create_result.errors}")
            return {
                'success': False,
                'error': f'Invoice creation failed: {create_result.errors}'
            }
        
        invoice = create_result.body.get('invoice', {})
        invoice_id = invoice.get('id')
        
        # Publish the invoice to make it available for payment
        publish_result = invoices_api.publish_invoice(
            invoice_id=invoice_id,
            body={
                "request_method": "EMAIL" if member_email else "SHARE_MANUALLY"
            }
        )
        
        if publish_result.is_error():
            logger.error(f"Error publishing Square invoice: {publish_result.errors}")
            return {
                'success': False,
                'error': f'Invoice publishing failed: {publish_result.errors}'
            }
        
        published_invoice = publish_result.body.get('invoice', {})
        public_url = published_invoice.get('public_url')
        
        logger.info(f"✅ Square invoice created successfully: {invoice_id}")
        
        return {
            'success': True,
            'invoice_id': invoice_id,
            'order_id': order_id,
            'public_url': public_url,
            'amount': amount,
            'currency': 'USD',
            'due_date': invoice_request['due_date'],
            'square_data': {
                'invoice': invoice,
                'order': order,
                'environment': creds['environment']
            }
        }
        
    except Exception as e:
        logger.error(f"Exception creating Square invoice: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def get_invoice_status(invoice_id: str) -> Dict[str, Any]:
    """
    Get the current status of a Square invoice.
    
    Args:
        invoice_id (str): Square invoice ID
        
    Returns:
        dict: Invoice status information
    """
    try:
        client = get_square_client()
        if not client:
            return {
                'success': False,
                'error': 'Could not initialize Square client'
            }
        
        invoices_api = client.invoices
        result = invoices_api.get_invoice(invoice_id=invoice_id)
        
        if result.is_error():
            return {
                'success': False,
                'error': f'Failed to get invoice: {result.errors}'
            }
        
        invoice = result.body.get('invoice', {})
        
        return {
            'success': True,
            'invoice_id': invoice_id,
            'status': invoice.get('status'),
            'invoice_data': invoice
        }
        
    except Exception as e:
        logger.error(f"Exception getting invoice status: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    """
    Create a Square invoice for a member with overdue payments.
    
    Args:
        member_name (str): Name of the member
        amount (float): Amount owed
        description (str): Description for the invoice
        
    Returns:
        str: Payment URL if successful, None if failed
    """
    try:
        print(f"INFO: Creating Square invoice for {member_name}, amount: ${amount:.2f}")
        
        # Initialize Square client
        client = get_square_client()
        if not client:
            print("ERROR: Could not initialize Square client")
            return None
        
        # Get location ID
        location_id = SQUARE_LOCATION_ID
        if not location_id:
            print("ERROR: Could not retrieve Square location ID. Please set SQUARE_LOCATION_ID environment variable")
            return None
        
        # Prepare invoice data
        invoice_data = {
            "invoice_request": {
                "request_method": "EMAIL",
                "request_type": "BALANCE",
                "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "primary_recipient": {
                    "name": member_name
                },
                "payment_requests": [
                    {
                        "request_method": "EMAIL",
                        "request_type": "BALANCE",
                        "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                    }
                ],
                "delivery_method": "EMAIL",
                "invoice_number": f"AF-{datetime.now().strftime('%Y%m%d')}-{member_name.replace(' ', '')[:10]}",
                "title": "Anytime Fitness - Overdue Account Balance",
                "description": f"{description} for {member_name}",
                "order": {
                    "location_id": location_id,
                    "line_items": [
                        {
                            "name": description,
                            "quantity": "1",
                            "item_type": "ITEM",
                            "base_price_money": {
                                "amount": int(amount * 100),  # Convert to cents
                                "currency": "USD"
                            }
                        }
                    ]
                }
            }
        }
        
        # Create the invoice
        invoices_api = client.invoices
        result = invoices_api.create_invoice(body=invoice_data)
        
        if result.is_success():
            invoice = result.body.get('invoice', {})
            invoice_id = invoice.get('id')
            print(f"SUCCESS: Created invoice {invoice_id} for {member_name}")
            
            # Publish the invoice to make it active
            try:
                publish_result = invoices_api.publish_invoice(
                    invoice_id=invoice_id,
                    body={
                        "request_method": "EMAIL"
                    }
                )
                
                if publish_result.is_success():
                    published_invoice = publish_result.body.get('invoice', {})
                    invoice_url = published_invoice.get('public_url', '')
                    print(f"SUCCESS: Published invoice with URL: {invoice_url}")
                    return invoice_url
                else:
                    print(f"ERROR: Failed to publish invoice: {publish_result.errors}")
                    return None
                    
            except Exception as publish_error:
                print(f"ERROR: Failed to publish invoice: {publish_error}")
                return None
                
        else:
            print(f"ERROR: Failed to create invoice: {result.errors}")
            return None
            
    except Exception as e:
        print(f"ERROR: Exception during invoice creation: {e}")
        return None


def test_square_connection():
    """Test Square connection"""
    client = get_square_client()
    if client:
        print("✅ Square connection successful")
        return True
    else:
        print("❌ Square connection failed")
        return False


def create_overdue_payment_message_with_invoice(member_name, membership_amount, late_fee=LATE_FEE_AMOUNT):
    """
    Creates an overdue payment message with Square invoice link.
    
    Args:
        member_name (str): Member's name
        membership_amount (float): Base membership amount owed
        late_fee (float): Late fee amount
    
    Returns:
        tuple: (message_text, invoice_url) or (None, None) if failed
    """
    total_amount = membership_amount + late_fee
    
    # Create Square invoice
    invoice_url = create_square_invoice(
        member_name=member_name,
        amount=total_amount, 
        description=f"Overdue Membership Payment + Late Fee"
    )
    
    if not invoice_url:
        print(f"ERROR: Could not create invoice for {member_name}")
        return None, None
    
    # Create message with invoice link
    message = f"""
🏃‍♂️ Hi {member_name},

Your Anytime Fitness membership payment is overdue. Please pay the following amount:

💰 Membership Amount: ${membership_amount:.2f}
⚠️ Late Fee: ${late_fee:.2f}
💳 Total Due: ${total_amount:.2f}

Pay securely online: {invoice_url}

Questions? Contact us at your local Anytime Fitness.

Thank you!
    """.strip()
    
    return message, invoice_url


# Alias for backward compatibility
create_invoice_for_member = create_square_invoice
