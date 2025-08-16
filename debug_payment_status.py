#!/usr/bin/env python3
"""
Debug script to test payment status lookup
"""

from clubos_training_api import ClubOSTrainingPackageAPI
import requests

def debug_payment_status():
    """Debug the payment status lookup"""
    print("🔍 Debugging payment status lookup...")
    
    # Initialize API
    api = ClubOSTrainingPackageAPI()
    
    # Test authentication
    print("🔐 Authenticating...")
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Test member ID
    member_id = "175560157"  # Dennis Rost
    print(f"🔍 Testing member ID: {member_id}")
    
    # Check what the member pages look like
    pages = [
        f"{api.base_url}/action/Members/view/{member_id}",
        f"{api.base_url}/action/Members/{member_id}",
        f"{api.base_url}/action/Agreements?memberId={member_id}",
    ]
    
    for i, url in enumerate(pages):
        print(f"\n📄 Testing page {i+1}: {url}")
        try:
            r = api.session.get(url, timeout=15)
            print(f"   Status: {r.status_code}")
            print(f"   Content length: {len(r.text)}")
            print(f"   Content: {repr(r.text)}")
            
            if r.status_code == 200:
                # Look for payment-related text
                text = r.text.lower()
                print(f"   Contains 'past due': {'past due' in text}")
                print(f"   Contains 'current': {'current' in text}")
                print(f"   Contains 'status': {'status' in text}")
                print(f"   Contains 'account': {'account' in text}")
                
                # Show a snippet around any payment-related text
                if 'past due' in text:
                    idx = text.find('past due')
                    snippet = text[max(0, idx-50):idx+50]
                    print(f"   Snippet around 'past due': {snippet}")
                
                if 'current' in text:
                    idx = text.find('current')
                    snippet = text[max(0, idx-50):idx+50]
                    print(f"   Snippet around 'current': {snippet}")
                    
            else:
                print(f"   ❌ Page not accessible")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test the actual method
    print(f"\n🔍 Testing get_member_payment_status method...")
    result = api.get_member_payment_status(member_id)
    print(f"   Result: {result}")

if __name__ == "__main__":
    debug_payment_status()
