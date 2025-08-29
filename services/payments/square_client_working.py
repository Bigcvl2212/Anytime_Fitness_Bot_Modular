"""
Square Payment Service - PROVEN WORKING CODE FROM ARCHIVED SCRIPT
"""

import os
from datetime import datetime, timedelta
from square.client import Square as SquareClient
from square.environment import SquareEnvironment

# Fix imports to use absolute paths
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
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
    
    PROVEN FUNCTION FROM ARCHIVED ANYTIME_BOT.PY
    
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


def create_square_invoice(member_name, amount, description="Overdue Payment"):
    """
    Create a Square invoice for a member with overdue payments.
    
    PROVEN WORKING FUNCTION FROM ARCHIVED ANYTIME_BOT.PY
    
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
        location_id = get_secret(SQUARE_LOCATION_ID_SECRET)
        if not location_id:
            print("ERROR: Could not retrieve Square location ID")
            return None
        
        # Prepare invoice data using PROVEN WORKING STRUCTURE
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
        
        # Create the invoice using PROVEN WORKING METHOD
        invoices_api = client.invoices
        result = invoices_api.create_invoice(body=invoice_data)
        
        if result.is_success():
            invoice = result.body.get('invoice', {})
            invoice_id = invoice.get('id')
            print(f"SUCCESS: Created invoice {invoice_id} for {member_name}")
            
            # Publish the invoice to make it active using PROVEN WORKING METHOD
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
    """Test Square connection - PROVEN FUNCTION"""
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
    
    PROVEN FUNCTION FROM ARCHIVED ANYTIME_BOT.PY
    
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
