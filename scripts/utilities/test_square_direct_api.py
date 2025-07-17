#!/usr/bin/env python3
"""
Test Square API directly with requests
"""

import requests
import json
from config.secrets_local import get_secret

# Square API configuration
SQUARE_API_BASE = "https://connect.squareup.com/v2"
SANDBOX_API_BASE = "https://connect.squareupsandbox.com/v2"

# Get credentials
sandbox_token = get_secret("square-sandbox-access-token")
sandbox_location = get_secret("square-sandbox-location-id")
production_token = get_secret("square-production-access-token")
production_location = get_secret("square-production-location-id")

def test_square_api_direct():
    """Test Square API directly with requests"""
    
    # Test sandbox first
    print("🔍 Testing Sandbox API...")
    headers = {
        "Square-Version": "2024-01-17",
        "Authorization": f"Bearer {sandbox_token}",
        "Content-Type": "application/json"
    }
    
    # Test locations endpoint
    try:
        resp = requests.get(f"{SANDBOX_API_BASE}/locations", headers=headers)
        print(f"Sandbox locations status: {resp.status_code}")
        if resp.status_code == 200:
            locations = resp.json()
            print(f"Found {len(locations.get('locations', []))} sandbox locations")
            for loc in locations.get('locations', []):
                print(f"  - {loc.get('name', 'Unknown')} (ID: {loc.get('id', 'Unknown')})")
        else:
            print(f"Sandbox error: {resp.text}")
    except Exception as e:
        print(f"Sandbox API error: {e}")
    
    # Test production
    print("\n🔍 Testing Production API...")
    headers["Authorization"] = f"Bearer {production_token}"
    
    try:
        resp = requests.get(f"{SQUARE_API_BASE}/locations", headers=headers)
        print(f"Production locations status: {resp.status_code}")
        if resp.status_code == 200:
            locations = resp.json()
            print(f"Found {len(locations.get('locations', []))} production locations")
            for loc in locations.get('locations', []):
                print(f"  - {loc.get('name', 'Unknown')} (ID: {loc.get('id', 'Unknown')})")
        else:
            print(f"Production error: {resp.text}")
    except Exception as e:
        print(f"Production API error: {e}")

def test_create_order_direct():
    """Test creating an order directly with the API"""
    print("\n🔍 Testing Order Creation...")
    
    # Use sandbox
    headers = {
        "Square-Version": "2024-01-17",
        "Authorization": f"Bearer {sandbox_token}",
        "Content-Type": "application/json"
    }
    
    order_data = {
        "order": {
            "location_id": sandbox_location,
            "line_items": [
                {
                    "name": "Test Item",
                    "base_price_money": {
                        "amount": 100,
                        "currency": "USD"
                    },
                    "quantity": "1"
                }
            ]
        }
    }
    
    try:
        resp = requests.post(f"{SANDBOX_API_BASE}/orders", headers=headers, json=order_data)
        print(f"Order creation status: {resp.status_code}")
        if resp.status_code == 200:
            order = resp.json()
            print(f"✅ Order created successfully!")
            print(f"Order ID: {order.get('order', {}).get('id')}")
            return order.get('order', {}).get('id')
        else:
            print(f"Order creation error: {resp.text}")
            return None
    except Exception as e:
        print(f"Order creation API error: {e}")
        return None

if __name__ == "__main__":
    test_square_api_direct()
    test_create_order_direct() 