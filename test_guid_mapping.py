#!/usr/bin/env python3
"""
Test the GUID mapping fix with Mark Benzinger
"""
import requests
import time

print("🧪 Testing GUID mapping fix with Mark Benzinger")
print(f"📋 Mark's data from database:")
print(f"  - Training table clubos_member_id: 125814462")  
print(f"  - Members table GUID: 66082049")
print(f"  - We should now use GUID 66082049 for ClubOS API calls")

try:
    # Test the individual package endpoint with Mark's clubos_member_id
    print(f"\n🔍 Testing /api/training-clients/125814462/packages...")
    start = time.time()
    response = requests.get('http://localhost:5000/api/training-clients/125814462/packages', timeout=30)
    end = time.time()
    
    print(f"⏱️ Response time: {end-start:.2f} seconds")
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data.get('success')}")
        print(f"📦 Active packages: {data.get('active_packages')}")
        print(f"💰 Past due: ${data.get('past_due_amount', 0):.2f}")
        print(f"💳 Payment status: {data.get('payment_status')}")
        
        if data.get('success') and data.get('active_packages'):
            if data.get('active_packages') != ['Training Package']:
                print("🎉 SUCCESS! We got real package names!")
            else:
                print("❌ Still getting generic package names")
        else:
            print("❌ API call succeeded but no packages found")
    else:
        print(f"❌ HTTP Error: {response.text[:300]}")
        
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*50)
print("📋 Test complete - check if we now get real package data!")
