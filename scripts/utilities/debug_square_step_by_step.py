#!/usr/bin/env python3
"""
Debug Square API step by step
"""

from square.client import Square
from config.secrets_local import get_secret

# Get credentials
token = get_secret("square-sandbox-access-token")
location_id = "LCR9E5HA00KPA"  # Test account location ID

print(f"Token starts with: {token[:10]}...")
print(f"Location ID: {location_id}")

# Test 1: Create client
print("\n🔍 Test 1: Creating Square client...")
try:
    client = Square(token=token)
    print("✅ Square client created successfully")
except Exception as e:
    print(f"❌ Failed to create client: {e}")
    exit(1)

# Test 2: List locations and get correct location ID
print("\n🔍 Test 2: Listing locations...")
try:
    locations = client.locations.list()
    print("✅ Locations API call successful")
    print(f"Locations result type: {type(locations)}")
    print(f"Locations result attributes: {[attr for attr in dir(locations) if not attr.startswith('_')]}")
    
    # Try different ways to access locations
    if hasattr(locations, 'locations'):
        locations_list = locations.locations
        print(f"✅ Found {len(locations_list)} locations via .locations")
    elif hasattr(locations, 'data'):
        locations_list = locations.data.get('locations', [])
        print(f"✅ Found {len(locations_list)} locations via .data")
    else:
        print(f"❌ Cannot access locations from response")
        print(f"Response dict: {locations.__dict__}")
        locations_list = []
    
    # Print available locations
    for i, loc in enumerate(locations_list):
        # Location objects have attributes, not dict keys
        loc_name = getattr(loc, 'name', 'Unknown')
        loc_id = getattr(loc, 'id', 'Unknown')
        print(f"  {i+1}. {loc_name} (ID: {loc_id})")
        
    # Use the first available location if we have one
    if locations_list:
        correct_location_id = getattr(locations_list[0], 'id', None)
        print(f"✅ Using location ID: {correct_location_id}")
        location_id = correct_location_id
    else:
        print("❌ No locations found")
        
except Exception as e:
    print(f"❌ Locations API failed: {e}")

# Test 3: Create order with correct location ID
print(f"\n🔍 Test 3: Creating order with location ID: {location_id}...")
try:
    order_request = {
        "location_id": location_id,
        "line_items": [
            {
                "name": "Test Item",
                "base_price_money": {"amount": 100, "currency": "USD"},
                "quantity": "1"
            }
        ]
    }
    
    order_result = client.orders.create(order=order_request)
    print("✅ Order created successfully!")
    print(f"Order result type: {type(order_result)}")
    print(f"Order result attributes: {[attr for attr in dir(order_result) if not attr.startswith('_')]}")
    
    # Try to get order ID
    if hasattr(order_result, 'order'):
        order_id = order_result.order.id
        print(f"✅ Order ID from .order.id: {order_id}")
    elif hasattr(order_result, 'data'):
        order_id = order_result.data['order']['id']
        print(f"✅ Order ID from .data: {order_id}")
    else:
        print(f"❌ Cannot find order ID in response")
        print(f"Response dict: {order_result.__dict__}")
        
except Exception as e:
    print(f"❌ Order creation failed: {e}")

print("\n🎯 Debug complete!") 