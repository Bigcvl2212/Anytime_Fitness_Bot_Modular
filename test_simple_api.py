#!/usr/bin/env python3

import requests
import json

def test_simple_api():
    """Test a simple API endpoint to see if authentication is working"""
    
    print("🧪 Testing Simple API Endpoints")
    print("=" * 50)
    
    try:
        # Test health endpoint (should work without auth)
        print("1. Testing health endpoint...")
        response = requests.get("http://localhost:5000/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Health endpoint working")
            print(f"   Response: {response.text}")
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
        
        # Test collections API
        print("\n2. Testing collections API...")
        response = requests.get("http://localhost:5000/api/collections/past-due", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("   ✅ Collections API working")
                print(f"   Response: {data}")
            except:
                print("   ⚠️ Collections API returned HTML instead of JSON")
                print(f"   Content preview: {response.text[:200]}...")
        else:
            print(f"   ❌ Collections API failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
        
        # Test members page
        print("\n3. Testing members page...")
        response = requests.get("http://localhost:5000/members", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        
        if response.status_code == 200:
            if 'login' in response.text.lower():
                print("   ⚠️ Members page returned login form (redirected)")
            else:
                print("   ✅ Members page working")
        else:
            print(f"   ❌ Members page failed: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to dashboard. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

if __name__ == "__main__":
    test_simple_api()
