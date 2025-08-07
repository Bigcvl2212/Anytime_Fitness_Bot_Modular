#!/usr/bin/env python3
"""
Find Dennis's package agreement IDs using the billing APIs we know work
"""

import sys
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
import json
import time

def find_dennis_agreement_ids():
    """Use the working billing API to find Dennis's package agreement IDs"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    # Dennis's known IDs from ClubHub and CSV
    dennis_ids_to_test = [
        65828815,    # ClubHub ID
        96530079,    # CSV agreement_agreementID  
        31489560,    # CSV userId
    ]
    
    print("🔍 Looking for Dennis's package agreement IDs using billing API...")
    
    for member_id in dennis_ids_to_test:
        print(f"\n🧪 Testing member ID: {member_id}")
        
        # Use the get_member_payment_status method that we know works
        try:
            payment_status = api.get_member_payment_status(str(member_id))
            
            if payment_status and payment_status != "Unknown":
                print(f"   ✅ Found payment status: {payment_status}")
                
                # Now try to get more detailed billing info using the billing endpoint
                billing_url = f"{api.base_url}/api/billing/member/{member_id}/billing_status"
                response = api.session.get(billing_url)
                print(f"   Billing status endpoint: {response.status_code}")
                
                if response.status_code == 200:
                    billing_data = response.json()
                    print(f"   Billing data keys: {list(billing_data.keys()) if isinstance(billing_data, dict) else 'Not a dict'}")
                    
                    # Look for agreement IDs in the billing data
                    billing_text = str(billing_data).lower()
                    if 'agreement' in billing_text or 'package' in billing_text:
                        print(f"   📦 Found agreement/package references in billing data:")
                        print(f"   {json.dumps(billing_data, indent=2)[:500]}...")
                    
                    # Check if there are any package agreement IDs
                    if isinstance(billing_data, dict):
                        for key, value in billing_data.items():
                            if 'agreement' in key.lower() or 'package' in key.lower():
                                print(f"   Agreement field {key}: {value}")
                
                # Also try the delegation + package list approach with this specific member
                print(f"   🔄 Testing delegation to member {member_id}...")
                api.session.cookies.set('delegatedUserId', str(member_id))
                
                list_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
                print(f"   Package list with delegation: {list_response.status_code}")
                
                if list_response.status_code == 200:
                    agreements = list_response.json()
                    print(f"   Found {len(agreements)} agreements when delegated to {member_id}")
                    
                    if agreements:
                        for i, agreement in enumerate(agreements):
                            agreement_id = agreement.get('id', 'No ID')
                            member_info = agreement.get('member', {})
                            member_name = member_info.get('name', 'No name')
                            print(f"   Agreement {i}: ID={agreement_id}, Member={member_name}")
                            
                            # Check if this agreement belongs to Dennis
                            if 'dennis' in member_name.lower() or 'rost' in member_name.lower():
                                print(f"   🎯 FOUND DENNIS AGREEMENT: {json.dumps(agreement, indent=2)}")
                                
                                # Try to get more details about this agreement
                                if agreement_id != 'No ID':
                                    print(f"   📋 Getting detailed info for agreement {agreement_id}...")
                                    
                                    # Try V2 endpoint
                                    v2_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/V2/{agreement_id}")
                                    print(f"   V2 endpoint: {v2_response.status_code}")
                                    if v2_response.status_code == 200:
                                        v2_data = v2_response.json()
                                        print(f"   V2 data: {json.dumps(v2_data, indent=2)[:300]}...")
                                    
                                    # Try billing status endpoint
                                    billing_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/{agreement_id}/billing_status")
                                    print(f"   Billing status: {billing_response.status_code}")
                                    if billing_response.status_code == 200:
                                        billing_data = billing_response.json()
                                        print(f"   Billing data: {json.dumps(billing_data, indent=2)[:300]}...")
                    
                # Reset delegation
                api.session.cookies.set('delegatedUserId', str(187032782))
                
            else:
                print(f"   ❌ No payment status found for member ID {member_id}")
                
        except Exception as e:
            print(f"   Error testing member ID {member_id}: {e}")
            
        time.sleep(1)
    
    # Also try searching by name using the members endpoint
    print(f"\n🔍 Searching for Dennis by name...")
    
    search_endpoints = [
        "/api/members/search",
        "/api/users/search", 
        "/api/prospects/search",
        "/api/clubservices/search"
    ]
    
    for endpoint in search_endpoints:
        try:
            # Try GET with query parameter
            response = api.session.get(f"{api.base_url}{endpoint}?q=dennis")
            print(f"   GET {endpoint}?q=dennis: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                data_text = str(data).lower()
                if 'dennis' in data_text or 'rost' in data_text:
                    print(f"   🎯 Found Dennis reference in {endpoint}!")
                    print(f"   Data: {json.dumps(data, indent=2)[:300]}...")
                    
            # Try POST with search payload
            search_payload = {"search": "Dennis Rost", "query": "Dennis", "name": "Dennis Rost"}
            response = api.session.post(f"{api.base_url}{endpoint}", json=search_payload)
            print(f"   POST {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                data_text = str(data).lower()
                if 'dennis' in data_text or 'rost' in data_text:
                    print(f"   🎯 Found Dennis reference in POST {endpoint}!")
                    print(f"   Data: {json.dumps(data, indent=2)[:300]}...")
                    
        except Exception as e:
            print(f"   Error with {endpoint}: {e}")

if __name__ == "__main__":
    print("🔍 Finding Dennis's package agreement IDs...")
    print("=" * 60)
    
    find_dennis_agreement_ids()
    
    print("\n" + "=" * 60)
    print("🏁 Search complete!")
