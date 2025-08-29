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
    # Correct imports for the installed Square SDK
    from square import Square as SquareClient  # type: ignore
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

# Constants
try:
    from config.constants import LATE_FEE_AMOUNT  # noqa: F401
except Exception:
    # Fallback default if constants not available; keeps import safe
    LATE_FEE_AMOUNT = 19.50

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
        Square: Configured Square client or None if failed
    """
    if not SQUARE_AVAILABLE:
        logger.error("Square SDK not available")
        return None
    try:
        from square.environment import SquareEnvironment
        
        creds = get_square_credentials()
        access_token = creds.get('access_token')
        if not access_token:
            logger.error("Missing Square access token")
            return None
            
        # Set environment
        env = str(creds.get('environment', 'sandbox')).lower()
        environment = SquareEnvironment.PRODUCTION if env == 'production' else SquareEnvironment.SANDBOX
        
        return SquareClient(token=access_token, environment=environment)
    except Exception as e:
        logger.error(f"Failed to create Square client: {e}")
        return None

def create_square_invoice(member_name: str, member_email: Optional[str] = None, amount: float = 0.0, description: str = "Training Package Payment") -> Dict[str, Any]:
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
            return {'success': False, 'error': 'Invalid member name or amount'}

        # Initialize Square client
        client = get_square_client()
        if not client:
            return {'success': False, 'error': 'Could not initialize Square client'}

        # Get credentials for location ID
        creds = get_square_credentials()
        location_id = creds.get('location_id')
        if not location_id:
            return {'success': False, 'error': 'Missing Square location ID'}

        # Step 1: Create or find customer
        name_parts = member_name.split(' ', 1)
        given_name = name_parts[0]
        family_name = name_parts[1] if len(name_parts) > 1 else ""
        
        # Use a default email if none provided (use valid domain)
        if member_email:
            email = member_email
        else:
            # Generate a valid-looking email for Square
            safe_name = given_name.lower().replace(' ', '') + '.' + family_name.lower().replace(' ', '')
            email = f"{safe_name}@members.anytimefitness.club"
        
        try:
            customer_result = client.customers.create(
                given_name=given_name,
                family_name=family_name,
                email_address=email
            )
            customer = customer_result.customer
            customer_id = customer.id
            logger.info(f"Created customer: {customer_id}")
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return {'success': False, 'error': f"Customer creation failed: {str(e)}"}

        # Step 2: Create order for the invoice
        order_request = {
            "location_id": location_id,
            "line_items": [
                {
                    "name": description,
                    "quantity": "1",
                    "base_price_money": {"amount": int(amount * 100), "currency": "USD"},
                }
            ],
        }
        
        try:
            order_result = client.orders.create(order=order_request)
            order = order_result.order
            order_id = order.id
            logger.info(f"Created order: {order_id}")
        except Exception as e:
            logger.error(f"Error creating Square order: {e}")
            return {'success': False, 'error': f"Order creation failed: {str(e)}"}

        # Step 3: Create invoice
        invoice_request_data = {
            "location_id": location_id,
            "order_id": order_id,
            "primary_recipient": {
                "customer_id": customer_id
            },
            "payment_requests": [
                {
                    "request_method": "EMAIL" if member_email else "SHARE_MANUALLY",
                    "request_type": "BALANCE",
                    "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                }
            ],
            "accepted_payment_methods": {
                "card": True,
                "square_gift_card": False,
                "bank_account": False,
                "buy_now_pay_later": False
            },
            "description": description,
            "invoice_number": f"AF-{datetime.now().strftime('%Y%m%d%H%M%S')}-{given_name[:5]}",
            "title": "Anytime Fitness Payment"
        }
        
        try:
            create_result = client.invoices.create(invoice=invoice_request_data)
            invoice = create_result.invoice
            invoice_id = invoice.id
            invoice_version = invoice.version
            logger.info(f"Created invoice: {invoice_id}")
        except Exception as e:
            logger.error(f"Error creating Square invoice: {e}")
            return {'success': False, 'error': f"Invoice creation failed: {str(e)}"}

        # Step 4: Publish the invoice
        try:
            publish_result = client.invoices.publish(
                invoice_id=invoice_id,
                version=invoice_version
            )
            published_invoice = publish_result.invoice
            public_url = getattr(published_invoice, 'public_url', None)
            logger.info(f"Published invoice with URL: {public_url}")
        except Exception as e:
            logger.error(f"Error publishing Square invoice: {e}")
            return {'success': False, 'error': f"Invoice publishing failed: {str(e)}"}

        logger.info(f"✅ Square invoice created successfully: {invoice_id}")
        return {
            'success': True,
            'invoice_id': invoice_id,
            'order_id': order_id,
            'customer_id': customer_id,
            'public_url': public_url,
            'amount': amount,
            'currency': 'USD',
            'due_date': (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            'square_data': {'invoice': invoice, 'order': order, 'customer': customer, 'environment': creds.get('environment')},
        }
    except Exception as e:
        logger.error(f"Exception creating Square invoice: {e}")
        return {'success': False, 'error': str(e)}

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
