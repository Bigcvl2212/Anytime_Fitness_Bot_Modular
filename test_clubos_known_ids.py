#!/usr/bin/env python3
"""
Test ClubOS training API with Jordan's known ClubOS ID
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_api import ClubOSTrainingPackageAPI

print("=== TESTING CLUBOS API WITH JORDAN'S KNOWN ID ===")

# Initialize ClubOS training API
api = ClubOSTrainingPackageAPI()
print("✅ ClubOS training API initialized")

# Test with Jordan's known ClubOS ID from the cache
jordan_clubos_id = "160402199"
print(f"🔍 Testing with Jordan's ClubOS ID: {jordan_clubos_id}")

try:
    payment_status = api.get_member_payment_status(jordan_clubos_id)
    
    if payment_status:
        print(f"✅ SUCCESS! Got payment status for Jordan:")
        print(f"   Payment Status: {payment_status}")
        print(f"   Data Type: {type(payment_status)}")
    else:
        print(f"❌ No payment status returned for Jordan")
        
except Exception as e:
    print(f"⚠️ Error: {str(e)}")

# Also test Dennis with a guess - maybe his ClubOS ID is his ClubHub ID
print(f"\n=== TESTING DENNIS WITH CLUBHUB ID ===")
dennis_clubhub_id = "65828815"
print(f"🔍 Testing Dennis with ClubHub ID: {dennis_clubhub_id}")

try:
    payment_status = api.get_member_payment_status(dennis_clubhub_id)
    
    if payment_status:
        print(f"✅ SUCCESS! Got payment status for Dennis:")
        print(f"   Payment Status: {payment_status}")
        print(f"   Data Type: {type(payment_status)}")
    else:
        print(f"❌ No payment status returned for Dennis")
        
except Exception as e:
    print(f"⚠️ Error: {str(e)}")

print(f"\nThis test confirms if the ClubOS training API works with known IDs")
