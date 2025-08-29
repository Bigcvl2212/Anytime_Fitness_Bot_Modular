#!/usr/bin/env python3
"""
Test Square Invoice Creation
"""
import os
import sys
sys.path.append('src')

from services.payments.square_client_simple import create_square_invoice

def test_invoice_creation():
    """Test creating a Square invoice with the new credentials"""
    print("🧾 TESTING SQUARE INVOICE CREATION")
    print("=" * 50)
    
    # Test invoice creation
    print("Creating test invoice...")
    
    result = create_square_invoice(
        member_name="John Test",
        member_email="john.test.valid@gmail.com",  # Use working email format
        amount=19.50,
        description="Test Anytime Fitness Late Fee"
    )
    
    print(f"\n📋 Invoice Creation Result:")
    print(f"Success: {result.get('success')}")
    
    if result.get('success'):
        print(f"✅ Invoice created successfully!")
        print(f"   - Invoice ID: {result.get('invoice_id')}")
        print(f"   - Order ID: {result.get('order_id')}")
        print(f"   - Amount: ${result.get('amount')}")
        print(f"   - Public URL: {result.get('public_url')}")
        print(f"   - Environment: {result.get('square_data', {}).get('environment')}")
    else:
        print(f"❌ Invoice creation failed:")
        print(f"   - Error: {result.get('error')}")
        
        # Check for specific error patterns
        error_msg = str(result.get('error', '')).lower()
        if '403' in error_msg and 'forbidden' in error_msg:
            print("   💡 This is a permissions error - the token needs additional scopes")
        elif 'location' in error_msg:
            print("   💡 Location ID issue - may need to use different location")
        elif 'unauthorized' in error_msg:
            print("   💡 Authorization issue - token may not have invoice permissions")

if __name__ == "__main__":
    test_invoice_creation()
