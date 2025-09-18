#!/usr/bin/env python3
"""
Test script to validate bulk check-in status API response format.
This will help debug the frontend tracking issue.
"""

import requests
import json
import sys
from datetime import datetime

def test_bulk_checkin_status():
    """Test the bulk check-in status endpoint to see what data it returns."""
    print("🔍 Testing Bulk Check-in Status API...")
    print(f"📅 Test time: {datetime.now()}")
    print("-" * 60)
    
    try:
        # Test the status endpoint
        print("📡 Making request to /api/bulk-checkin-status...")
        response = requests.get('http://localhost:8000/api/bulk-checkin-status', timeout=10)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("\n✅ JSON Response received:")
                print(json.dumps(data, indent=2, default=str))
                
                # Validate expected structure
                print("\n🔍 Validating response structure...")
                
                if 'success' in data:
                    print(f"  ✅ Has 'success' field: {data['success']}")
                else:
                    print("  ❌ Missing 'success' field")
                
                if 'status' in data:
                    print(f"  ✅ Has 'status' field")
                    status = data['status']
                    
                    # Check key fields frontend expects
                    key_fields = ['total_members', 'processed_members', 'total_checkins', 'ppv_excluded']
                    for field in key_fields:
                        if field in status:
                            print(f"  ✅ status.{field}: {status[field]}")
                        else:
                            print(f"  ❌ Missing status.{field}")
                else:
                    print("  ❌ Missing 'status' field")
                    print("  🔍 Available top-level fields:", list(data.keys()) if data else 'None')
                
                # Check if this looks like a direct status response (old format)
                if 'total_members' in data and 'status' not in data:
                    print("\n⚠️  Response appears to be in old direct format!")
                    print("  Frontend expects: {success: true, status: {...}}")
                    print("  But received: {total_members: ..., processed_members: ...}")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"Raw response: {response.text[:500]}")
                return False
        else:
            print(f"❌ HTTP error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - Flask server is not running")
        print("💡 Start the server with: python run_dashboard.py")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_api_availability():
    """Test if the main API is available."""
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        print(f"🌐 Main endpoint status: {response.status_code}")
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🚀 Bulk Check-in Status API Test")
    print("=" * 60)
    
    # Check if server is running
    if not test_api_availability():
        print("❌ Server not responding. Please start the Flask server first.")
        sys.exit(1)
    
    # Test the status endpoint
    success = test_bulk_checkin_status()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test completed successfully!")
        print("💡 Check the response structure above to debug frontend issues.")
    else:
        print("❌ Test failed!")
        print("💡 Fix the API endpoint or server issues before testing frontend.")
    
    print("\n📋 Next Steps:")
    print("1. Ensure response has {success: true, status: {...}} structure")
    print("2. Check that status object contains: total_members, processed_members, total_checkins, ppv_excluded")
    print("3. Test frontend bulk check-in functionality")