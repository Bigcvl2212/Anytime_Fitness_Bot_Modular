#!/usr/bin/env python3
"""
Test Square Customer + Invoice workflow
"""
import os
import sys
sys.path.append('src')

from src.services.payments.square_client_simple import get_square_client, get_square_credentials
from datetime import datetime, timedelta

def create_customer_and_invoice():
    """Create a customer first, then create an invoice for them"""
    print("👤 CREATING CUSTOMER + INVOICE WORKFLOW")
    print("=" * 50)
    
    client = get_square_client()
    creds = get_square_credentials()
    location_id = creds.get('location_id')
    
    try:
        # Step 1: Create a customer
        print("1. Creating customer...")
        customer_request = {
            "given_name": "John",
            "family_name": "Test",
            "email_address": "john.test@example.com"
        }
        
        customer_result = client.customers.create(
            given_name="John",
            family_name="Test",
            email_address="john.test.valid@gmail.com"  # Use a more standard email
        )
        customer = customer_result.customer
        customer_id = customer.id
        print(f"✅ Customer created: {customer_id}")
        
        # Step 2: Create order
        print("2. Creating order...")
        order_request = {
            "location_id": location_id,
            "line_items": [{
                "name": "Anytime Fitness Late Fee",
                "quantity": "1", 
                "base_price_money": {"amount": 1950, "currency": "USD"}
            }]
        }
        
        order_result = client.orders.create(order=order_request)
        order = order_result.order
        order_id = order.id
        print(f"✅ Order created: {order_id}")
        
        # Step 3: Create invoice with customer_id
        print("3. Creating invoice...")
        invoice_request = {
            "location_id": location_id,
            "order_id": order_id,
            "primary_recipient": {
                "customer_id": customer_id
            },
            "payment_requests": [{
                "request_method": "EMAIL",
                "request_type": "BALANCE",
                "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            }],
            "accepted_payment_methods": {
                "card": True,
                "square_gift_card": False,
                "bank_account": False,
                "buy_now_pay_later": False
            },
            "invoice_number": f"AF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": "Anytime Fitness Payment"
        }
        
        invoice_result = client.invoices.create(invoice=invoice_request)
        invoice = invoice_result.invoice
        invoice_id = invoice.id
        print(f"✅ Invoice created: {invoice_id}")
        
        # Step 4: Publish invoice
        print("4. Publishing invoice...")
        publish_result = client.invoices.publish(
            invoice_id=invoice_id,
            version=invoice.version
        )
        
        published_invoice = publish_result.invoice
        public_url = getattr(published_invoice, 'public_url', 'No URL available')
        print(f"✅ Invoice published!")
        print(f"   Public URL: {public_url}")
        print(f"   Customer: {customer.given_name} {customer.family_name}")
        print(f"   Email: {customer.email_address}")
        
        return {
            'success': True,
            'customer_id': customer_id,
            'order_id': order_id,
            'invoice_id': invoice_id,
            'public_url': public_url
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # Extract detailed error info
        if hasattr(e, 'body') and isinstance(e.body, dict):
            errors = e.body.get('errors', [])
            for error in errors:
                print(f"   - Category: {error.get('category')}")
                print(f"   - Code: {error.get('code')}")
                print(f"   - Detail: {error.get('detail')}")
                print(f"   - Field: {error.get('field', 'N/A')}")
        
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    result = create_customer_and_invoice()
    
    if result['success']:
        print(f"\n🎉 COMPLETE SUCCESS!")
        print(f"Square Invoice workflow is fully operational!")
    else:
        print(f"\n❌ Workflow failed: {result.get('error')}")
