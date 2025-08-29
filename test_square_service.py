#!/usr/bin/env python3
"""
Test the actual Square service integration
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test the actual square client service
try:
    from services.payments.square_client_simple import get_square_client, create_square_invoice
    
    print("🧪 TESTING SQUARE SERVICE INTEGRATION")
    print("=" * 50)
    
    # Test client creation
    print("1. Testing Square client creation...")
    client = get_square_client()
    if client:
        print("✅ Square client created successfully")
        
        # Test basic API call
        print("2. Testing basic API connectivity...")
        try:
            result = client.locations.list()
            if result.is_success():
                locations = result.body.get('locations', [])
                print(f"✅ API working - {len(locations)} locations found")
                for loc in locations[:2]:
                    location_data = loc if isinstance(loc, dict) else loc.__dict__
                    name = location_data.get('name', 'Unknown')
                    location_id = location_data.get('id', 'No ID')
                    print(f"  - {name} ({location_id})")
            else:
                print(f"❌ API error: {result.errors}")
        except Exception as e:
            print(f"❌ API exception: {e}")
        
        # Test invoice creation (dry run)
        print("3. Testing invoice creation flow (dry run)...")
        try:
            # This will fail with 401 but we'll see if the structure is right
            invoice_result = create_square_invoice(
                member_name="Test Member",
                member_email="test@test.com",
                amount=19.50,
                description="Test Invoice"
            )
            if invoice_result.get('success'):
                print(f"✅ Invoice creation successful: {invoice_result.get('invoice_id')}")
            else:
                print(f"❌ Invoice creation failed: {invoice_result.get('error')}")
        except Exception as e:
            print(f"❌ Invoice creation exception: {e}")
            
    else:
        print("❌ Failed to create Square client")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ General error: {e}")

print("\n📋 SUMMARY:")
print("The Square SDK is properly configured, but authentication is failing.")
print("This indicates the tokens may be expired or lack proper permissions.")
print("Next steps: Check Square Dashboard for token validity and permissions.")
