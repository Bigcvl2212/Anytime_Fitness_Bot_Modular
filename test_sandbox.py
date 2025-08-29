#!/usr/bin/env python3
"""
Test Square with Sandbox Environment
"""
import os
import sys
sys.path.append('src')

# Force sandbox environment
os.environ['SQUARE_ENVIRONMENT'] = 'sandbox'

from services.payments.square_client_simple import get_square_credentials, get_square_client

def test_sandbox():
    print("🧪 Testing Square API in SANDBOX mode")
    print("="*50)
    
    creds = get_square_credentials()
    print(f"Environment: {creds.get('environment')}")
    print(f"Access Token: {creds.get('access_token', '')[:20]}...")
    print(f"Location ID: {creds.get('location_id')}")
    
    client = get_square_client()
    if not client:
        print("❌ Could not create Square client")
        return
        
    try:
        # Test locations API in sandbox
        locations_api = client.locations
        result = locations_api.list()
        
        if result.is_error():
            print(f"❌ Sandbox API Error: {result.errors}")
        else:
            locations = result.body.get('locations', [])
            print(f"✅ Sandbox authentication successful!")
            print(f"   - Found {len(locations)} location(s)")
            for loc in locations:
                print(f"   - Location: {loc.get('name', 'Unnamed')} ({loc.get('id')})")
                
        # If locations work, test a simple invoice creation
        if not result.is_error():
            print(f"\n🧪 Testing invoice creation in sandbox...")
            from services.payments.square_client_simple import create_square_invoice
            
            invoice_result = create_square_invoice(
                member_name="Sandbox Test User",
                member_email="test@sandbox.example.com",
                amount=1.00,  # $1.00 test
                description="Sandbox Test Invoice"
            )
            
            if invoice_result.get('success'):
                print(f"✅ Sandbox invoice created: {invoice_result.get('invoice_id')}")
            else:
                print(f"❌ Sandbox invoice failed: {invoice_result.get('error')}")
                
    except Exception as e:
        print(f"❌ Exception in sandbox test: {e}")

if __name__ == "__main__":
    test_sandbox()
