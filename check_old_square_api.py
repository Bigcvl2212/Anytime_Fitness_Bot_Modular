#!/usr/bin/env python3

"""Check Square SDK v21 API structure for proper method calls"""

import inspect
from square.client import Client

try:
    client = Client(access_token="dummy")
    
    print("=== CUSTOMERS API ===")
    customer_methods = [method for method in dir(client.customers) if not method.startswith('_')]
    for method in customer_methods:
        print(f"  - {method}")
    
    if hasattr(client.customers, 'create_customer'):
        sig = inspect.signature(client.customers.create_customer)
        print(f"create_customer signature: {sig}")
    
    print("\n=== ORDERS API ===")
    order_methods = [method for method in dir(client.orders) if not method.startswith('_')]
    for method in order_methods:
        print(f"  - {method}")
    
    if hasattr(client.orders, 'create_order'):
        sig = inspect.signature(client.orders.create_order)
        print(f"create_order signature: {sig}")
    
    print("\n=== INVOICES API ===")
    invoice_methods = [method for method in dir(client.invoices) if not method.startswith('_')]
    for method in invoice_methods:
        print(f"  - {method}")
    
    if hasattr(client.invoices, 'create_invoice'):
        sig = inspect.signature(client.invoices.create_invoice)
        print(f"create_invoice signature: {sig}")
    
    if hasattr(client.invoices, 'publish_invoice'):
        sig = inspect.signature(client.invoices.publish_invoice)
        print(f"publish_invoice signature: {sig}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()