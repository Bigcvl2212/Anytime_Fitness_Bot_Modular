#!/usr/bin/env python3
"""
Test correct Square Invoice API structure
"""
import os
import sys
sys.path.append('src')

from src.services.payments.square_client_simple import get_square_client, get_square_credentials
from datetime import datetime, timedelta

def test_simple_invoice():
    """Test with minimal invoice structure following Square API docs"""
    print("🧾 TESTING MINIMAL SQUARE INVOICE")
    print("=" * 40)
    
    client = get_square_client()
    creds = get_square_credentials()
    location_id = creds.get('location_id')
    
    print(f"Using location: {location_id}")
    
    try:
        # Step 1: Create a simple order
        print("1. Creating order...")
        order_request = {
            "location_id": location_id,
            "line_items": [
                {
                    "name": "Test Late Fee",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 1950,  # $19.50 in cents
                        "currency": "USD"
                    }
                }
            ]
        }
        
        order_result = client.orders.create(order=order_request)
        order = order_result.order
        order_id = order.id
        print(f"✅ Order created: {order_id}")
        
        # Step 2: Create invoice with minimal structure
        print("2. Creating invoice...")
        invoice_request = {
            "location_id": location_id,
            "order_id": order_id,
            "primary_recipient": {
                "name": "John Test"  # This might be the wrong field
            },
            "payment_requests": [
                {
                    "request_method": "SHARE_MANUALLY",
                    "request_type": "BALANCE",
                    "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                }
            ],
            "invoice_number": f"AF-TEST-{datetime.now().strftime('%Y%m%d%H%M')}",
            "title": "Test Invoice"
        }
        
        invoice_result = client.invoices.create(invoice=invoice_request)
        invoice = invoice_result.invoice
        invoice_id = invoice.id
        print(f"✅ Invoice created: {invoice_id}")
        
        # Step 3: Publish the invoice
        print("3. Publishing invoice...")
        publish_result = client.invoices.publish(
            invoice_id=invoice_id,
            version=invoice.version
        )
        
        published_invoice = publish_result.invoice
        public_url = getattr(published_invoice, 'public_url', 'No URL')
        print(f"✅ Invoice published!")
        print(f"   Public URL: {public_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # Try to extract detailed error info
        if hasattr(e, 'body') and isinstance(e.body, dict):
            errors = e.body.get('errors', [])
            for error in errors:
                print(f"   - Field: {error.get('field', 'Unknown')}")
                print(f"   - Detail: {error.get('detail', 'No detail')}")
                print(f"   - Code: {error.get('code', 'No code')}")
        
        return False

def test_invoice_field_formats():
    """Test different primary_recipient formats"""
    print("\n🔍 TESTING DIFFERENT RECIPIENT FORMATS")
    print("=" * 40)
    
    client = get_square_client()
    creds = get_square_credentials()
    location_id = creds.get('location_id')
    
    # Different recipient formats to try
    recipient_formats = [
        {"name": "John Test"},
        {"display_name": "John Test"},
        {"given_name": "John", "family_name": "Test"},
        {"display_name": "John Test", "email_address": "test@example.com"}
    ]
    
    for i, recipient in enumerate(recipient_formats, 1):
        print(f"\n{i}. Testing recipient format: {recipient}")
        
        try:
            # Create simple order
            order_request = {
                "location_id": location_id,
                "line_items": [{
                    "name": f"Test Item {i}",
                    "quantity": "1",
                    "base_price_money": {"amount": 100, "currency": "USD"}
                }]
            }
            
            order_result = client.orders.create(order=order_request)
            order_id = order_result.order.id
            
            # Try invoice with this recipient format
            invoice_request = {
                "location_id": location_id,
                "order_id": order_id,
                "primary_recipient": recipient,
                "payment_requests": [{
                    "request_method": "SHARE_MANUALLY",
                    "request_type": "BALANCE",
                    "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                }],
                "invoice_number": f"AF-FORMAT-{i}",
                "title": f"Format Test {i}"
            }
            
            invoice_result = client.invoices.create(invoice=invoice_request)
            print(f"   ✅ SUCCESS with format: {recipient}")
            return recipient  # Return the working format
            
        except Exception as e:
            print(f"   ❌ Failed with format {recipient}")
            if hasattr(e, 'body') and 'errors' in e.body:
                error = e.body['errors'][0]
                print(f"      Error: {error.get('detail', str(e))}")

if __name__ == "__main__":
    # First try the simple test
    if not test_simple_invoice():
        # If it fails, try different formats
        working_format = test_invoice_field_formats()
        if working_format:
            print(f"\n✅ Found working recipient format: {working_format}")
        else:
            print("\n❌ No working recipient format found")
