"""
Square Payment Service - FIXED WITH CURRENT API STRUCTURE
"""

import os
from datetime import datetime, timedelta
from square.client import Square as SquareClient
from square.environment import SquareEnvironment

# Try relative imports first, fall back to absolute imports
try:
    from ...config.constants import (
        SQUARE_ENVIRONMENT,
        SQUARE_SANDBOX_ACCESS_TOKEN_SECRET,
        SQUARE_PRODUCTION_ACCESS_TOKEN_SECRET,
        SQUARE_LOCATION_ID_SECRET,
        LATE_FEE_AMOUNT,
        YELLOW_RED_MESSAGE_TEMPLATE
    )
    from ...config.secrets import get_secret
except ImportError:
    import sys
    import os
    # Add root directory to path for absolute imports
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, root_dir)
    
    from config.constants import (
        SQUARE_ENVIRONMENT,
        SQUARE_SANDBOX_ACCESS_TOKEN_SECRET,
        SQUARE_PRODUCTION_ACCESS_TOKEN_SECRET,
        SQUARE_LOCATION_ID_SECRET,
        LATE_FEE_AMOUNT,
        YELLOW_RED_MESSAGE_TEMPLATE
    )
    from config.secrets import get_secret


def get_square_client():
    """
    Get configured Square client instance.
    
    Returns:
        SquareClient: Configured Square client or None if failed
    """
    try:
        access_token = get_secret(
            SQUARE_SANDBOX_ACCESS_TOKEN_SECRET if SQUARE_ENVIRONMENT == 'sandbox' 
            else SQUARE_PRODUCTION_ACCESS_TOKEN_SECRET
        )
        
        if not access_token:
            print("ERROR: Missing Square access token")
            return None
            
        environment = SquareEnvironment.SANDBOX if SQUARE_ENVIRONMENT == 'sandbox' else SquareEnvironment.PRODUCTION
        return SquareClient(
            token=access_token,
            environment=environment
        )
    except Exception as e:
        print(f"ERROR: Failed to create Square client: {e}")
        return None


def create_square_invoice(member_name, amount, description="Overdue Payment", email=None):
    """
    Create a Square invoice for a member with overdue payments.
    
    Uses current Square API structure from official documentation.
    
    Args:
        member_name (str): Name of the member
        amount (float): Amount owed
        description (str): Description for the invoice
        email (str): Member's email address (optional, will use placeholder if not provided)
        
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
        
        # Get location ID dynamically or use production location ID
        if SQUARE_ENVIRONMENT == 'production':
            location_id = "Q0TK7D7CFHWE3"  # Your production location ID
        else:
            location_id = get_secret(SQUARE_LOCATION_ID_SECRET)
            if not location_id or location_id.startswith('default_'):
                # Try to get location dynamically
                try:
                    locations_api = client.locations
                    locations_result = locations_api.list_locations()
                    if locations_result.is_success() and locations_result.body.get('locations'):
                        location_id = locations_result.body['locations'][0]['id']
                        print(f"SUCCESS: Using dynamic location ID: {location_id}")
                    else:
                        print("ERROR: No locations found")
                        return None
                except Exception as e:
                    print(f"ERROR: Could not retrieve Square location ID: {e}")
                    return None
        
        print(f"INFO: Using location ID: {location_id}")
        
        # Create order first (required for invoice)
        order_request = {
            "location_id": location_id,
            "line_items": [
                {
                    "name": f"{description} - {member_name}",
                    "base_price_money": {
                        "amount": int(amount * 100),  # Convert to cents
                        "currency": "USD"
                    },
                    "quantity": "1"
                }
            ]
        }
        
        orders_api = client.orders
        order_result = orders_api.create_order(body={"order": order_request})
        
        if not order_result.is_success():
            print(f"ERROR: Failed to create order: {order_result.errors}")
            return None
            
        order_id = order_result.body['order']['id']
        print(f"SUCCESS: Created order with ID: {order_id}")
        
        # Create customer first if email is provided
        customer_id = None
        if email and '@' in email:
            try:
                customers_api = client.customers
                customer_request = {
                    "given_name": member_name.split()[0] if ' ' in member_name else member_name,
                    "family_name": member_name.split()[-1] if len(member_name.split()) > 1 else "",
                    "email_address": email
                }
                customer_result = customers_api.create_customer(body=customer_request)
                if customer_result.is_success():
                    customer_id = customer_result.body['customer']['id']
                    print(f"SUCCESS: Created customer with ID: {customer_id}")
            except Exception as e:
                print(f"WARN: Could not create customer: {e}")
        
        # Create invoice using current API structure
        invoice_data = {
            "location_id": location_id,
            "order_id": order_id,
            "payment_requests": [
                {
                    "request_type": "BALANCE",
                    "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                }
            ],
            "delivery_method": "EMAIL",
            "invoice_number": f"AF-{datetime.now().strftime('%Y%m%d%H%M%S')}-{member_name.replace(' ', '')[:10]}",
            "title": "Anytime Fitness - Overdue Account Balance",
            "description": f"{description} for {member_name}",
            "accepted_payment_methods": {
                "card": True,
                "square_gift_card": False,
                "bank_account": False,
                "buy_now_pay_later": False,
                "cash_app_pay": False
            }
        }
        
        # Add recipient info
        if customer_id:
            invoice_data["primary_recipient"] = {"customer_id": customer_id}
        else:
            invoice_data["primary_recipient"] = {
                "given_name": member_name.split()[0] if ' ' in member_name else member_name,
                "family_name": member_name.split()[-1] if len(member_name.split()) > 1 else ""
            }
        
        # Create the invoice
        invoices_api = client.invoices
        result = invoices_api.create_invoice(body={"invoice": invoice_data})
        
        if result.is_success():
            invoice = result.body.get('invoice', {})
            invoice_id = invoice.get('id')
            invoice_version = invoice.get('version', 0)
            
            print(f"SUCCESS: Square invoice created with ID: {invoice_id}")
            
            # Get the latest version before publishing (to avoid version mismatch)
            try:
                import time
                time.sleep(1)  # Small delay to ensure invoice is ready
                get_result = invoices_api.get_invoice(invoice_id=invoice_id)
                if get_result.is_success():
                    latest_invoice = get_result.body.get('invoice', {})
                    invoice_version = latest_invoice.get('version', invoice_version)
                    print(f"SUCCESS: Got latest invoice version: {invoice_version}")
            except Exception as e:
                print(f"WARN: Could not get latest invoice version: {e}")
            
            # Publish the invoice to make it payable
            publish_result = invoices_api.publish_invoice(
                invoice_id=invoice_id,
                body={"request_version": invoice_version}
            )
            
            if publish_result.is_success():
                published_invoice = publish_result.body.get('invoice', {})
                payment_url = published_invoice.get('public_url')
                
                if payment_url:
                    print(f"SUCCESS: Invoice published. Payment URL: {payment_url}")
                    return payment_url
                else:
                    print("WARN: Invoice published but no payment URL returned")
                    return None
            else:
                print(f"ERROR: Failed to publish invoice: {publish_result.errors}")
                return None
        else:
            print(f"ERROR: Failed to create Square invoice: {result.errors}")
            return None
            
    except Exception as e:
        print(f"ERROR: Exception creating Square invoice for {member_name}: {e}")
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
    message = YELLOW_RED_MESSAGE_TEMPLATE.format(
        member_name=member_name,
        membership_amount=membership_amount,
        late_fee=late_fee,
        total_amount=total_amount,
        invoice_link=invoice_url
    )
    
    return message, invoice_url


# Alias for backward compatibility
create_invoice_for_member = create_square_invoice
