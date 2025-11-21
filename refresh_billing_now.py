#!/usr/bin/env python3
"""Hit the refresh billing endpoint to update past due amounts"""

import requests
import time

print("🔄 Refreshing billing data via Flask API...")

try:
    # Wait for Flask to start
    time.sleep(2)
    
    # Hit the refresh endpoint
    response = requests.post('http://localhost:5000/api/refresh-billing-data', timeout=120)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Billing refresh complete!")
        print(f"   Members synced: {result.get('members_synced', 0)}")
        print(f"   Billing data updated: {result.get('billing_updated', 0)}")
    else:
        print(f"❌ Refresh failed: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
