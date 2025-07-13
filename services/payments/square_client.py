"""
Square Payment Integration - ENHANCED WITH EXPERIMENTAL FEATURES
Combines verified working code with advanced experimental features from Anytime_Bot_Complete.py
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any

# Square SDK
from square import Square
from square.environment import SquareEnvironment
from square.core.api_error import ApiError

from ...config.constants import SQUARE_ENVIRONMENT, SQUARE_ACCESS_TOKEN_SECRET, YELLOW_RED_MESSAGE_TEMPLATE, LATE_FEE_AMOUNT


class EnhancedSquareClient:
    """
    Enhanced Square client with comprehensive invoice creation and payment processing.
    Based on verified working code with experimental features from Anytime_Bot_Complete.py
    """
    
    def __init__(self, access_token: str = None):
        """Initialize Square client with enhanced functionality"""
        self.access_token = access_token or self._get_access_token()
        self.environment = self._get_environment()
        self.client = self._initialize_client()
        
    def _get_access_token(self) -> str:
        """Get Square access token from secret manager"""
        try:
            from google.cloud import secretmanager
            client = secretmanager.SecretManagerServiceClient()
            name = f"{SQUARE_ACCESS_TOKEN_SECRET}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            print(f"❌ Error getting Square access token: {e}")
            return None
    
    def _get_environment(self) -> SquareEnvironment:
        """Get Square environment (sandbox or production)"""
        env = os.getenv("SQUARE_ENVIRONMENT", SQUARE_ENVIRONMENT)
        return SquareEnvironment.SANDBOX if env.lower() == "sandbox" else SquareEnvironment.PRODUCTION
    
    def _initialize_client(self) -> Square:
        """Initialize Square client"""
        if not self.access_token:
            raise ValueError("Square access token is required")
        
        return Square(
            environment=self.environment,
            token=self.access_token
        )
    
    def create_comprehensive_invoice(self, member_data: Dict[str, Any], amount: float, 
                                   description: str = "Gym Payment", 
                                   due_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Create comprehensive invoice with enhanced features from experimental code.
        
        ENHANCED WITH EXPERIMENTAL FEATURES FROM ANYTIME_BOT_COMPLETE.PY
        """
        try:
            print(f"💳 Creating comprehensive invoice for {member_data.get('name', 'Unknown')}")
            
            # Prepare invoice data
            invoice_data = {
                "order_id": f"gym_payment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "primary_recipient": {
                    "customer_id": member_data.get('member_id', ''),
                    "email_address": member_data.get('email', ''),
                    "name": member_data.get('name', 'Unknown')
                },
                "payment_requests": [
                    {
                        "request_type": "INVOICE",
                        "due_date": (due_date or datetime.now() + timedelta(days=7)).isoformat(),
                        "tipping_enabled": False,
                        "automatic_payment_source": "NONE",
                        "reminders": [
                            {
                                "relative_scheduled_days": 3,
                                "message_template": "Your gym payment of ${amount} is due in 3 days."
                            },
                            {
                                "relative_scheduled_days": 1,
                                "message_template": "Your gym payment of ${amount} is due tomorrow."
                            }
                        ]
                    }
                ],
                "delivery_method": "EMAIL",
                "invoice": {
                    "title": f"Anytime Fitness - {description}",
                    "description": f"Payment for {description}",
                    "scheduled_date": datetime.now().isoformat(),
                    "public_url": None,
                    "next_payment_amount_money": {
                        "amount": int(amount * 100),  # Convert to cents
                        "currency": "USD"
                    }
                }
            }
            
            # Create invoice
            response = self.client.invoices.create_invoice(invoice_data)
            
            if response.is_success():
                invoice = response.body.get('invoice', {})
                print(f"✅ Invoice created successfully: {invoice.get('id', 'Unknown')}")
                
                return {
                    'success': True,
                    'invoice_id': invoice.get('id'),
                    'invoice_url': invoice.get('public_url'),
                    'amount': amount,
                    'member_name': member_data.get('name'),
                    'created_at': datetime.now().isoformat()
                }
            else:
                print(f"❌ Failed to create invoice: {response.errors}")
                return {
                    'success': False,
                    'error': str(response.errors),
                    'amount': amount,
                    'member_name': member_data.get('name')
                }
                
        except ApiError as e:
            print(f"❌ Square API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'amount': amount,
                'member_name': member_data.get('name')
            }
        except Exception as e:
            print(f"❌ Unexpected error creating invoice: {e}")
            return {
                'success': False,
                'error': str(e),
                'amount': amount,
                'member_name': member_data.get('name')
            }
    
    def publish_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """
        Publish invoice to make it available for payment.
        
        ENHANCED WITH EXPERIMENTAL FEATURES FROM ANYTIME_BOT_COMPLETE.PY
        """
        try:
            print(f"📤 Publishing invoice: {invoice_id}")
            
            response = self.client.invoices.publish_invoice(invoice_id)
            
            if response.is_success():
                invoice = response.body.get('invoice', {})
                print(f"✅ Invoice published successfully")
                
                return {
                    'success': True,
                    'invoice_id': invoice_id,
                    'public_url': invoice.get('public_url'),
                    'status': invoice.get('status'),
                    'published_at': datetime.now().isoformat()
                }
            else:
                print(f"❌ Failed to publish invoice: {response.errors}")
                return {
                    'success': False,
                    'error': str(response.errors),
                    'invoice_id': invoice_id
                }
                
        except ApiError as e:
            print(f"❌ Square API error publishing invoice: {e}")
            return {
                'success': False,
                'error': str(e),
                'invoice_id': invoice_id
            }
        except Exception as e:
            print(f"❌ Unexpected error publishing invoice: {e}")
            return {
                'success': False,
                'error': str(e),
                'invoice_id': invoice_id
            }
    
    def create_and_publish_invoice(self, member_data: Dict[str, Any], amount: float,
                                  description: str = "Gym Payment") -> Dict[str, Any]:
        """
        Create and publish invoice in one step.
        
        ENHANCED WITH EXPERIMENTAL FEATURES FROM ANYTIME_BOT_COMPLETE.PY
        """
        try:
            # Step 1: Create invoice
            create_result = self.create_comprehensive_invoice(member_data, amount, description)
            
            if not create_result.get('success'):
                return create_result
            
            # Step 2: Publish invoice
            invoice_id = create_result.get('invoice_id')
            publish_result = self.publish_invoice(invoice_id)
            
            if publish_result.get('success'):
                # Combine results
                return {
                    'success': True,
                    'invoice_id': invoice_id,
                    'public_url': publish_result.get('public_url'),
                    'amount': amount,
                    'member_name': member_data.get('name'),
                    'status': publish_result.get('status'),
                    'created_at': create_result.get('created_at'),
                    'published_at': publish_result.get('published_at')
                }
            else:
                return {
                    'success': False,
                    'error': f"Created but failed to publish: {publish_result.get('error')}",
                    'invoice_id': invoice_id,
                    'amount': amount,
                    'member_name': member_data.get('name')
                }
                
        except Exception as e:
            print(f"❌ Error in create_and_publish_invoice: {e}")
            return {
                'success': False,
                'error': str(e),
                'amount': amount,
                'member_name': member_data.get('name')
            }
    
    def get_invoice_status(self, invoice_id: str) -> Dict[str, Any]:
        """Get current status of an invoice"""
        try:
            response = self.client.invoices.get_invoice(invoice_id)
            
            if response.is_success():
                invoice = response.body.get('invoice', {})
                return {
                    'success': True,
                    'invoice_id': invoice_id,
                    'status': invoice.get('status'),
                    'amount_paid': invoice.get('amount_paid_money', {}).get('amount', 0),
                    'total_amount': invoice.get('total_amount_money', {}).get('amount', 0),
                    'public_url': invoice.get('public_url')
                }
            else:
                return {
                    'success': False,
                    'error': str(response.errors),
                    'invoice_id': invoice_id
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'invoice_id': invoice_id
            }
    
    def cancel_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Cancel an invoice"""
        try:
            response = self.client.invoices.cancel_invoice(invoice_id)
            
            if response.is_success():
                return {
                    'success': True,
                    'invoice_id': invoice_id,
                    'cancelled_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': str(response.errors),
                    'invoice_id': invoice_id
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'invoice_id': invoice_id
            }


# Convenience functions for backward compatibility
def create_square_invoice(member_name: str, member_email: str, amount_due: float, 
                         description: str = "Gym Payment") -> Dict[str, Any]:
    """Create Square invoice with enhanced features"""
    client = EnhancedSquareClient()
    member_data = {
        'name': member_name,
        'email': member_email,
        'member_id': f"member_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    return client.create_and_publish_invoice(member_data, amount_due, description)


def publish_square_invoice(invoice_id: str) -> Dict[str, Any]:
    """Publish Square invoice"""
    client = EnhancedSquareClient()
    return client.publish_invoice(invoice_id)


# --- STUBS FOR BACKWARD COMPATIBILITY ---
def get_square_client():
    """Return an instance of EnhancedSquareClient with correct access token and environment."""
    return EnhancedSquareClient()


def test_square_connection():
    """Test the Square API connection by listing locations. Returns True if successful, False otherwise."""
    try:
        client = EnhancedSquareClient()
        # Try to list locations as a simple test
        locations_api = client.client.locations
        response = locations_api.list_locations()
        if response.is_success():
            print("✅ Square connection test successful. Locations found:")
            for loc in response.body.get('locations', []):
                print(f"   - {loc.get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Square connection test failed: {response.errors}")
            return False
    except Exception as e:
        print(f"❌ Square connection test error: {e}")
        return False


def create_overdue_payment_message_with_invoice(member_name, amount_due, late_fee, invoice_url):
    """Generate an overdue payment message using the template and provided values."""
    try:
        total_amount = float(amount_due) + float(late_fee)
        message = YELLOW_RED_MESSAGE_TEMPLATE.format(
            member_name=member_name,
            membership_amount=float(amount_due),
            late_fee=float(late_fee),
            total_amount=total_amount,
            invoice_link=invoice_url
        )
        return message
    except Exception as e:
        print(f"❌ Error creating overdue payment message: {e}")
        return f"Hi {member_name}, your payment is overdue. Please pay here: {invoice_url}"
