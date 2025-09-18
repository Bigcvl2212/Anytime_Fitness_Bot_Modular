#!/usr/bin/env python3

"""Test Square SDK method signatures"""

import inspect
from square.client import Client

try:
    client = Client(access_token="dummy")
    
    # Check method signatures
    print("publish_invoice signature:")
    sig = inspect.signature(client.invoices.publish_invoice)
    print(f"  {sig}")
    
    print("\ncreate_invoice signature:")
    sig = inspect.signature(client.invoices.create_invoice)
    print(f"  {sig}")
    
    print("\ncreate_customer signature:")
    sig = inspect.signature(client.customers.create_customer)
    print(f"  {sig}")
    
    print("\ncreate_order signature:")
    sig = inspect.signature(client.orders.create_order)
    print(f"  {sig}")
    
except Exception as e:
    print(f"Error: {e}")