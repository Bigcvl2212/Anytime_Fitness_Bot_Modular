#!/usr/bin/env python3
"""
Simple script to test ClubOS service status
"""
import requests
import json

def test_clubos_status():
    """Test ClubOS service status via API"""
    try:
        base_url = "http://localhost:5000"
        
        # First check if there's a clubos status endpoint
        endpoints_to_try = [
            "/api/clubos/status",
            "/api/auth/clubos/status", 
            "/health"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                print(f"📡 Testing {endpoint}...")
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'clubos' in str(data).lower() or endpoint == '/health':
                            print(f"   Response: {json.dumps(data, indent=2)[:300]}...")
                    except:
                        print(f"   Response: {response.text[:200]}...")
                print()
            except Exception as e:
                print(f"   Error: {e}\n")
        
        # Also test calendar events to see if ClubOS is working there
        print("📅 Testing calendar events endpoint...")
        try:
            response = requests.get(f"{base_url}/api/calendar/events", timeout=10)
            print(f"   Calendar events status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Events count: {len(data.get('events', []))}")
                if 'error' in str(data).lower():
                    print(f"   Error in response: {data}")
        except Exception as e:
            print(f"   Calendar error: {e}")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_clubos_status()