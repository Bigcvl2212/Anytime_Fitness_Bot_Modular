#!/usr/bin/env python3

"""Test Square invoice creation to debug response structure"""

import sys
import os
sys.path.append('src/services/authentication')
from secure_secrets_manager import SecureSecretsManager
from square.client import Client

try:
    # Get credentials
    secrets_manager = SecureSecretsManager()
    access_token = secrets_manager.get_secret("square-production-access-token")
    location_id = secrets_manager.get_secret("square-production-location-id")
    
    if not access_token or not location_id:
        print("❌ Missing credentials")
        exit(1)
        
    client = Client(access_token=access_token)
    
    # Create a simple customer first
    print("1. Creating customer...")
    customer_result = client.customers.create_customer(
        body={
            "given_name": "Test",
            "family_name": "Customer",
            "email_address": "test@example.com"
        }
    )
    print(f"Customer result type: {type(customer_result)}")
    print(f"Customer result dir: {[attr for attr in dir(customer_result) if not attr.startswith('_')]}")
    
    if hasattr(customer_result, 'body'):
        print(f"Customer result body: {customer_result.body}")
        customer_id = customer_result.body["customer"]["id"]
        print(f"✅ Customer ID: {customer_id}")
    else:
        print("❌ No body attribute")
        exit(1)
    
    # Create a simple order
    print("\n2. Creating order...")
    order_result = client.orders.create_order(
        body={
            "order": {
                "location_id": location_id,
                "line_items": [
                    {
                        "name": "Test Item",
                        "quantity": "1",
                        "base_price_money": {
                            "amount": 1000,  # $10.00
                            "currency": "USD"
                        }
                    }
                ]
            }
        }
    )
    print(f"Order result type: {type(order_result)}")
    print(f"Order result dir: {[attr for attr in dir(order_result) if not attr.startswith('_')]}")
    
    if hasattr(order_result, 'body'):
        print(f"Order result body: {order_result.body}")
        order_id = order_result.body["order"]["id"]
        print(f"✅ Order ID: {order_id}")
    else:
        print("❌ No body attribute")
        exit(1)
    
    # Test invoice creation
    print("\n3. Creating invoice...")
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
                    "due_date": "2025-09-25"
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
    
    print(f"Invoice request: {invoice_request}")
    
    invoice_result = client.invoices.create_invoice(
        body=invoice_request
    )
    
    print(f"Invoice result type: {type(invoice_result)}")
    print(f"Invoice result dir: {[attr for attr in dir(invoice_result) if not attr.startswith('_')]}")
    
    if hasattr(invoice_result, 'body'):
        print(f"Invoice result body: {invoice_result.body}")
        if 'invoice' in invoice_result.body:
            invoice_id = invoice_result.body["invoice"]["id"]
            print(f"✅ Invoice ID: {invoice_id}")
        else:
            print(f"❌ No 'invoice' key in body. Available keys: {list(invoice_result.body.keys())}")
    else:
        print("❌ No body attribute")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()