#!/usr/bin/env python3
"""
Debug Square API to see what methods are available
"""

from services.payments.square_client_fixed import get_square_client
from config.secrets_local import get_secret

def debug_square_client():
    """Debug the Square client to see available methods"""
    print("🔍 DEBUGGING SQUARE CLIENT...")
    
    # Test getting the client
    client = get_square_client()
    if not client:
        print("❌ Could not get Square client")
        return
    
    print("✅ Square client created successfully")
    
    # Check what APIs are available
    print("\n📋 Available APIs:")
    for attr in dir(client):
        if not attr.startswith('_'):
            print(f"  - {attr}")
    
    # Check orders API specifically
    if hasattr(client, 'orders'):
        orders_api = client.orders
        print(f"\n📋 Orders API methods:")
        for attr in dir(orders_api):
            if not attr.startswith('_'):
                print(f"  - {attr}")
    else:
        print("❌ No orders API found")
    
    # Check invoices API
    if hasattr(client, 'invoices'):
        invoices_api = client.invoices
        print(f"\n📋 Invoices API methods:")
        for attr in dir(invoices_api):
            if not attr.startswith('_'):
                print(f"  - {attr}")
    else:
        print("❌ No invoices API found")

if __name__ == "__main__":
    debug_square_client() 