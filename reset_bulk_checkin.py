#!/usr/bin/env python3
"""
Emergency script to reset bulk check-in status
"""

import requests
import json

def reset_bulk_checkin():
    """Reset bulk check-in status via API call"""
    try:
        # Try to reset via API
        response = requests.post('http://localhost:5000/api/bulk-checkin-reset', timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Reset successful: {result.get('message', 'Unknown')}")
        else:
            print(f"❌ Reset failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Flask app not running - status will be reset when app starts")
    except Exception as e:
        print(f"❌ Error resetting bulk check-in: {e}")

def check_status():
    """Check current bulk check-in status"""
    try:
        response = requests.get('http://localhost:5000/api/bulk-checkin-status', timeout=5)
        
        if response.status_code == 200:
            status = response.json()
            print(f"Current status: {status.get('status', 'unknown')}")
            print(f"Is running: {status.get('is_running', 'unknown')}")
            print(f"Message: {status.get('message', 'No message')}")
        else:
            print(f"❌ Status check failed: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Flask app not running")
    except Exception as e:
        print(f"❌ Error checking status: {e}")

if __name__ == "__main__":
    print("🔍 Checking current bulk check-in status...")
    check_status()
    
    print("\n🚨 Attempting to reset bulk check-in...")
    reset_bulk_checkin()
    
    print("\n🔍 Checking status after reset...")
    check_status()
