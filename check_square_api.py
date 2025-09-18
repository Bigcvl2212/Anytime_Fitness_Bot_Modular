#!/usr/bin/env python3

"""Quick script to check Square SDK API methods"""

try:
    from square.client import Client
    
    # Create a dummy client to inspect the API methods
    client = Client(access_token="dummy_token")
    
    print("Customer API methods:")
    customer_methods = [method for method in dir(client.customers) if not method.startswith('_')]
    for method in customer_methods:
        print(f"  - {method}")
    
    print("\nOrder API methods:")
    order_methods = [method for method in dir(client.orders) if not method.startswith('_')]
    for method in order_methods:
        print(f"  - {method}")
    
    print("\nInvoice API methods:")
    invoice_methods = [method for method in dir(client.invoices) if not method.startswith('_')]
    for method in invoice_methods:
        print(f"  - {method}")
        
except Exception as e:
    print(f"Error checking Square SDK: {e}")