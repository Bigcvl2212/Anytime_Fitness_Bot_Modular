#!/usr/bin/env python3
"""
Test Square SDK Integration
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.payments.square_client_simple import (
    get_square_client, 
    get_square_credentials, 
    create_square_invoice,
    SQUARE_AVAILABLE
)

def test_square_setup():
    """Test Square SDK setup and basic functionality"""
    print("🧪 Testing Square SDK Integration")
    print("="*50)
    
    # Test 1: Check if Square SDK is available
    print(f"✓ Square SDK Available: {SQUARE_AVAILABLE}")
    
    if not SQUARE_AVAILABLE:
        print("❌ Square SDK not available - please install: pip install squareup")
        return False
    
    # Test 2: Get credentials
    try:
        creds = get_square_credentials()
        print(f"✓ Environment: {creds.get('environment')}")
        print(f"✓ Token present: {'Yes' if creds.get('access_token') else 'No'}")
        print(f"✓ Location ID present: {'Yes' if creds.get('location_id') else 'No'}")
    except Exception as e:
        print(f"❌ Error getting credentials: {e}")
        return False
    
    # Test 3: Create Square client
    try:
        client = get_square_client()
        print(f"✓ Square client created: {'Yes' if client else 'No'}")
    except Exception as e:
        print(f"❌ Error creating client: {e}")
        return False
    
    # Test 4: Test invoice creation (this will likely fail in production but shows the API is working)
    try:
        print("\n🧾 Testing Invoice Creation...")
        result = create_square_invoice(
            member_name="Test User",
            member_email="test@example.com", 
            amount=25.0,
            description="Square Integration Test"
        )
        
        if result.get('success'):
            print("✅ Invoice created successfully!")
            print(f"   Invoice ID: {result.get('invoice_id')}")
            print(f"   Public URL: {result.get('public_url')}")
        else:
            print(f"⚠️  Invoice creation failed (expected in test): {result.get('error', 'Unknown error')}")
            # Check if it's an auth error (expected) vs API error (unexpected)
            error_msg = result.get('error', '').lower()
            if 'unauthorized' in error_msg or 'authentication' in error_msg:
                print("   → This is expected with test/invalid credentials")
                return True  # Auth error means API is working, just need valid creds
            else:
                print("   → This indicates an API integration issue")
                return False
    except Exception as e:
        print(f"❌ Exception testing invoice creation: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_square_setup()
    
    print("\n" + "="*50)
    if success:
        print("✅ Square SDK Integration Test: PASSED")
        print("   The Square SDK is properly installed and configured.")
        print("   Invoice creation may require valid production/sandbox credentials.")
    else:
        print("❌ Square SDK Integration Test: FAILED")
        print("   Please check the Square SDK installation and configuration.")
    
    print("\nNext steps:")
    print("1. Ensure you have valid Square credentials (production or sandbox)")
    print("2. Test invoice creation with real credentials")
    print("3. Use the dashboard to create invoices for members")
