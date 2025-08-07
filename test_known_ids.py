#!/usr/bin/env python3
"""
Test if we can use known information to find ClubOS IDs
"""

print("=== TESTING CLUBOS ID DISCOVERY ===")

# We know from the funding cache that Jordan's ClubOS ID is 160402199
# We know from master contact list that Jordan's email is JORDAN_KRUEGER_23@HOTMAIL.COM
# We know from master contact list that Dennis's email is djrost74@gmail.com

# Let's test if we can use the cached ClubOS training API with Jordan's known ID
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_api import ClubOSTrainingPackageAPI

print("✅ Testing ClubOS training API with Jordan's cached ClubOS ID...")

api = ClubOSTrainingPackageAPI()
jordan_clubos_id = "160402199"  # From funding_status_cache

try:
    payment_status = api.get_member_payment_status(jordan_clubos_id)
    
    if payment_status:
        print(f"✅ SUCCESS! Jordan's ClubOS training data:")
        print(f"   ClubOS ID: {jordan_clubos_id}")
        print(f"   Payment Status: {payment_status}")
        print(f"   Data Type: {type(payment_status)}")
        
        # Now try Dennis with his ClubHub ID as a guess
        print(f"\n🔍 Testing Dennis with his ClubHub ID as ClubOS ID...")
        dennis_clubhub_id = "65828815"
        
        dennis_payment_status = api.get_member_payment_status(dennis_clubhub_id)
        
        if dennis_payment_status:
            print(f"✅ SUCCESS! Dennis found with ClubHub ID as ClubOS ID:")
            print(f"   ClubOS ID: {dennis_clubhub_id}")
            print(f"   Payment Status: {dennis_payment_status}")
        else:
            print(f"❌ Dennis not found using ClubHub ID as ClubOS ID")
            
    else:
        print(f"❌ No payment status for Jordan's known ClubOS ID")
        
except Exception as e:
    print(f"⚠️ Error: {str(e)}")

print(f"\n📋 Summary:")
print(f"Jordan's ClubHub ID: 44871105")
print(f"Jordan's ClubOS ID: 160402199 (from cache)")
print(f"Dennis's ClubHub ID: 65828815")
print(f"Dennis's ClubOS ID: Unknown")
