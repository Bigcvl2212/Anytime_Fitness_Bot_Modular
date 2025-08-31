"""
Square Invoice Client - Built from scratch using current SDK documentation
"""

import logging
from datetime import datetime, timedelta
from square.client import Square
from square.core.api_error import ApiError
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from secrets_local import get_secret

logger = logging.getLogger(__name__)

def get_square_client():
    """Get configured Square client instance"""
    try:
        # Use PRODUCTION credentials
        access_token = get_secret("square-production-access-token")
        client = Square(
            token=access_token
        )
        return client
    except Exception as e:
        logger.error(f"❌ Error creating Square client: {e}")
        return None

def create_square_invoice(member_name, contact_info, amount, description, delivery_method="email"):
    """
    Create and send Square invoice using ONLY current SDK documentation
    
    Args:
        member_name: Name of the member
        contact_info: Email address or phone number
        amount: Invoice amount in dollars
        description: Invoice description
        delivery_method: "email" or "sms"
    
    Returns:
        dict: Success/error response
    """
    try:
        logger.info(f"📧 Creating Square invoice for {member_name}: ${amount} via {delivery_method} to {contact_info}")
        
        # Initialize Square client
        client = get_square_client()
        if not client:
            return {
                'success': False,
                'error': 'Could not initialize Square client',
                'message': f"Failed to create invoice for {member_name}"
            }
        
        # Get location ID
        location_id = get_secret("square-production-location-id")
        if not location_id:
            return {
                'success': False,
                'error': 'Could not retrieve Square location ID',
                'message': f"Failed to create invoice for {member_name}"
            }
        
        # Step 1: Create customer
        name_parts = member_name.split()
        first_name = name_parts[0] if name_parts else "Customer"
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        customer_data = {
            "given_name": first_name,
            "family_name": last_name,
        }
        
        # Add contact info based on delivery method
        if delivery_method == "sms":
            # For SMS delivery, use phone number and placeholder email
            customer_data["phone_number"] = contact_info
            customer_data["email_address"] = f"{first_name.lower()}.{last_name.lower()}@anytimefitness.com"
        else:
            # For EMAIL delivery, use the actual email from database
            customer_data["email_address"] = contact_info
            
        try:
            customer_result = client.customers.create(**customer_data)
            customer_id = customer_result.customer.id
        except ApiError as e:
            logger.error(f"❌ Failed to create customer: {e}")
            return {
                'success': False,
                'error': f"Failed to create customer: {e}",
                'message': f"Failed to create invoice for {member_name}"
            }
        logger.info(f"✅ Created customer {customer_id} for {member_name}")
        
        # Step 2: Create order using SDK example structure
        order_data = {
            "location_id": location_id,
            "line_items": [
                {
                    "name": description[:100],
                    "quantity": "1",
                    "base_price_money": {
                        "amount": int(amount * 100),  # Convert to cents
                        "currency": "USD"
                    }
                }
            ]
        }
        
        try:
            order_result = client.orders.create(order=order_data)
            order_id = order_result.order.id
        except ApiError as e:
            logger.error(f"❌ Failed to create order: {e}")
            return {
                'success': False,
                'error': f"Failed to create order: {e}",
                'message': f"Failed to create invoice for {member_name}"
            }
        logger.info(f"✅ Created order {order_id}")
        
        # Step 3: Create invoice using older SDK structure
        invoice_request = {
            "invoice": {
                "location_id": location_id,
                "order_id": order_id,
                "primary_recipient": {
                    "customer_id": customer_id
                },
                "payment_requests": [
                    {
                        "request_type": "BALANCE",
                        "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                    }
                ],
                "delivery_method": "EMAIL",  # SMS not supported in current Square API
                "invoice_number": f"AF-{datetime.now().strftime('%Y%m%d%H%M%S')}-{member_name.replace(' ', '')[:10]}",
                "title": "Anytime Fitness - Overdue Account Balance",
                "description": description,
                # "scheduled_at": (datetime.now() + timedelta(hours=1)).isoformat() + "Z",  # Not needed
                "accepted_payment_methods": {
                    "card": True,
                    "square_gift_card": False,
                    "bank_account": False,
                    "buy_now_pay_later": False,
                    "cash_app_pay": False
                }
            }
        }
        
        # Create invoice using newer SDK method
        try:
            invoice_result = client.invoices.create(invoice=invoice_request["invoice"])
            invoice_id = invoice_result.invoice.id
            invoice_version = invoice_result.invoice.version
        except ApiError as e:
            logger.error(f"❌ Failed to create invoice: {e}")
            return {
                'success': False,
                'error': f"Failed to create invoice: {e}",
                'message': f"Failed to create invoice for {member_name}"
            }
        logger.info(f"✅ Created invoice {invoice_id} for {member_name}")
        
        # Step 4: Publish invoice using newer SDK method
        try:
            publish_result = client.invoices.publish(
                invoice_id=invoice_id,
                version=invoice_version
            )
        except ApiError as e:
            logger.error(f"❌ Failed to publish invoice: {e}")
            return {
                'success': False,
                'error': f"Failed to publish invoice: {e}",
                'message': f"Failed to create invoice for {member_name}"
            }
                
        logger.info(f"✅ Published invoice successfully")
        
        # Return success response
        return {
            'success': True,
            'invoice_id': invoice_id,
            'public_url': f"https://squareup.com/invoice/{invoice_id}",
            'message': f"Successfully created and published invoice for {member_name}"
        }
        
    except Exception as e:
        logger.error(f"❌ Exception during invoice creation: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to create invoice for {member_name}"
        }
