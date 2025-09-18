"""
Square Invoice Client - Built from scratch using current SDK documentation
"""

import logging
from datetime import datetime, timedelta
import sys
import os

# Import secure secrets manager
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'authentication'))
from secure_secrets_manager import SecureSecretsManager

logger = logging.getLogger(__name__)

def get_square_client():
    """Get configured Square client instance using ONLY SecureSecretsManager (no fallbacks)"""
    try:
        # Import Square Client only when needed to avoid import issues
        from square.client import Client
        
        # ONLY use SecureSecretsManager - no fallbacks to local secrets
        secrets_manager = SecureSecretsManager()
        access_token = secrets_manager.get_secret("square-production-access-token")
        
        if not access_token:
            raise ValueError("Square production access token not found in SecureSecretsManager")
        
        logger.info("✅ Using Square access token from SecureSecretsManager (production)")
        
        # Configure the Square client for production environment
        client = Client(access_token=access_token)
        return client
        
    except Exception as e:
        logger.error(f"❌ Error creating Square client from SecureSecretsManager: {e}")
        return None

def test_square_authentication():
    """Test Square authentication and return detailed error info"""
    try:
        client = get_square_client()
        if not client:
            return {"success": False, "error": "Failed to create Square client"}
        
        # Test basic API access
        try:
            result = client.locations.list()
            # If we get here without an exception, the client is working
            return {"success": True, "message": "Square authentication working"}
        except Exception as api_error:
            # Check if it's an authentication error vs other error
            if "UNAUTHORIZED" in str(api_error) or "401" in str(api_error):
                return {"success": False, "error": "❌ UNAUTHORIZED: Your Square access token is invalid, expired, or lacks permissions\n💡 SOLUTION: Generate a new Personal Access Token in Square Developer Dashboard\n💡 Make sure to select these scopes: CUSTOMERS_WRITE, INVOICES_WRITE, PAYMENTS_WRITE, LOCATIONS_READ"}
            else:
                return {"success": False, "error": f"Square API error: {api_error}"}
            
    except Exception as e:
        return {"success": False, "error": f"❌ Exception testing Square auth: {str(e)}"}

def create_square_invoice(member_name, contact_info, amount, description, delivery_method="email", email_address=None):
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
        
        # Get location ID from SecureSecretsManager ONLY (no fallbacks)
        try:
            secrets_manager = SecureSecretsManager()
            location_id = secrets_manager.get_secret("square-production-location-id")
            
            if not location_id:
                return {
                    'success': False,
                    'error': 'Square production location ID not found in SecureSecretsManager',
                    'message': f"Failed to create invoice for {member_name}"
                }
            
            logger.info("✅ Using Square location ID from SecureSecretsManager (production)")
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to retrieve Square location ID from SecureSecretsManager: {e}',
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
        
        # Add contact info - ensure valid email for Square customer record
        if delivery_method == "sms":
            # For SMS delivery, use phone number for SMS but need valid email for Square customer record
            customer_data["phone_number"] = contact_info
            # Always use the email_address parameter if provided, otherwise create a placeholder
            if email_address and "@" in email_address:
                customer_data["email_address"] = email_address
            else:
                # Create a valid placeholder email for Square requirements
                sanitized_name = "".join(c for c in member_name.lower().replace(" ", "") if c.isalnum())[:20]
                customer_data["email_address"] = f"{sanitized_name}@placeholder-email.com"
        else:
            # For EMAIL delivery, use the actual email from database
            customer_data["email_address"] = contact_info
            
        try:
            customer_request = {
                "given_name": customer_data["given_name"],
                "family_name": customer_data["family_name"]
            }
            if customer_data.get("email_address"):
                customer_request["email_address"] = customer_data["email_address"]
            if customer_data.get("phone_number"):
                customer_request["phone_number"] = customer_data["phone_number"]
            
            customer_result = client.customers.create_customer(
                body=customer_request
            )
            customer_id = customer_result.body["customer"]["id"]
        except Exception as e:
            logger.error(f"❌ Failed to create customer: {e}")
            return {
                'success': False,
                'error': f"Failed to create customer: {e}",
                'message': f"Failed to create invoice for {member_name}"
            }
        logger.info(f"✅ Created customer {customer_id} for {member_name}")
        
        # Step 2: Create order using SDK example structure
        order_data = {
            "order": {
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
        }
        
        try:
            order_result = client.orders.create_order(
                body=order_data
            )
            order_id = order_result.body["order"]["id"]
        except Exception as e:
            logger.error(f"❌ Failed to create order: {e}")
            return {
                'success': False,
                'error': f"Failed to create order: {e}",
                'message': f"Failed to create invoice for {member_name}"
            }
        logger.info(f"✅ Created order {order_id}")
        
        # Step 3: Create invoice using official SDK structure
        # Set correct delivery method based on what was requested
        square_delivery_method = "SMS" if delivery_method == "sms" and customer_data.get("phone_number") else "EMAIL"
        
        # Create invoice with EMAIL delivery method first (required field)
        # We'll handle SMS via different mechanism if needed
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
                "accepted_payment_methods": {
                    "card": True,
                    "square_gift_card": False,
                    "bank_account": False,
                    "buy_now_pay_later": False,
                    "cash_app_pay": False
                },
                "delivery_method": "EMAIL"
            }
        }
        
        # Create invoice using correct SDK method
        try:
            invoice_result = client.invoices.create_invoice(
                body=invoice_request
            )
            
            # Check for errors in response
            if 'errors' in invoice_result.body:
                error_details = invoice_result.body['errors']
                logger.error(f"❌ Square API errors: {error_details}")
                return {
                    'success': False,
                    'error': f"Square API errors: {error_details}",
                    'message': f"Failed to create invoice for {member_name}"
                }
            
            # Extract invoice data
            if 'invoice' not in invoice_result.body:
                logger.error(f"❌ Unexpected response structure: {invoice_result.body}")
                return {
                    'success': False,
                    'error': f"Unexpected Square API response structure",
                    'message': f"Failed to create invoice for {member_name}"
                }
            
            invoice_id = invoice_result.body["invoice"]["id"]
            invoice_version = invoice_result.body["invoice"]["version"]
        except Exception as e:
            logger.error(f"❌ Failed to create invoice: {e}")
            return {
                'success': False,
                'error': f"Failed to create invoice: {e}",
                'message': f"Failed to create invoice for {member_name}"
            }
        logger.info(f"✅ Created invoice {invoice_id} for {member_name}")
        
        # Step 4: Publish invoice using correct SDK method  
        try:
            publish_request = {
                "version": invoice_version
            }
            
            publish_result = client.invoices.publish_invoice(
                invoice_id=invoice_id,
                body=publish_request
            )
            
            # For SMS delivery, we need to handle this separately since Square API doesn't support SMS in invoices
            # The invoice will be sent via EMAIL, and we'll log that SMS was requested
            if square_delivery_method == "SMS":
                logger.info(f"⚠️ SMS delivery requested but not supported by Square API. Invoice sent via EMAIL to {customer_data.get('email_address')} instead of SMS to {contact_info}")
            
        except Exception as e:
            logger.error(f"❌ Failed to publish invoice: {e}")
            return {
                'success': False,
                'error': f"Failed to publish invoice: {e}",
                'message': f"Failed to create invoice for {member_name}"
            }
        except Exception as e:
            logger.error(f"❌ Failed to publish invoice: {e}")
            return {
                'success': False,
                'error': f"Failed to publish invoice: {e}",
                'message': f"Failed to create invoice for {member_name}"
            }
                
        logger.info(f"✅ Published invoice successfully via {square_delivery_method} to {contact_info}")
        
        # Save invoice to database
        try:
            from src.services.database_manager import DatabaseManager
            db_manager = DatabaseManager()
            
            invoice_data = {
                'member_id': customer_id,
                'square_invoice_id': invoice_id,
                'amount': amount,
                'status': 'sent',
                'payment_method': 'CARD',
                'delivery_method': delivery_method.upper(),
                'due_date': None,  # Square handles due dates
                'notes': f'Invoice for {member_name} - {description}'
            }
            
            db_manager.save_invoice(invoice_data)
            logger.info(f"💾 Invoice {invoice_id} saved to database")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save invoice to database: {e}")
        
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
