#!/usr/bin/env python3
"""Test the old V2 system that was working to get invoice data"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubos_api_client import ClubOSAPIAuthentication
from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI
from src.config.clubhub_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD

def test_old_v2_system():
    """Test using the old working V2 system from comprehensive_data_pull_WORKING.py"""
    
    # Test with Miguel who shows Past Due in bare list (billingState: 4)
    member_id = "177673765"
    
    print(f"🔍 Testing old V2 system for member {member_id}")
    
    # Initialize ClubOS authentication using the old system
    auth = ClubOSAPIAuthentication()
    
    try:
        # Authenticate
        print("🔐 Authenticating with ClubOS...")
        success = auth.login(CLUBOS_USERNAME, CLUBOS_PASSWORD)
        if not success:
            print("❌ Authentication failed")
            return
        
        print("✅ Authentication successful")
        
        # Get the authenticated headers
        headers = auth.get_headers()
        print(f"📋 Auth headers: {list(headers.keys())}")
        
        # Now test getting agreements for this member using breakthrough method
        training_api = ClubOSTrainingPackageAPI()
        
        print("\n📊 Testing breakthrough method first...")
        packages = training_api.get_member_training_packages_breakthrough(member_id)
        
        if packages:
            print(f"✅ Breakthrough method found {len(packages)} packages")
            print(f"📊 Packages data: {packages}")
            if isinstance(packages, list) and len(packages) > 0 and isinstance(packages[0], dict):
                for pkg in packages:
                    print(f"  - Agreement {pkg['agreement_id']}: {pkg['package_name']} - {pkg['payment_status']} - ${pkg.get('biweekly_amount', 0):.2f}")
            else:
                print(f"📊 Raw packages data structure: {type(packages)} = {packages}")
        else:
            print("❌ Breakthrough method found no packages")
            return
        
        # Now test V2 endpoint using old working method
        print("\n📄 Testing V2 endpoint with old system...")
        import requests
        
        for pkg in packages:
            agreement_id = pkg['agreement_id']
            print(f"\n🔍 Testing V2 for agreement {agreement_id}")
            
            # Use the exact method from comprehensive_data_pull_WORKING.py
            url = f"https://anytime.club-os.com/api/agreements/package_agreements/V2/{agreement_id}"
            params = {
                'include': ['invoices', 'scheduledPayments', 'prohibitChangeTypes']
            }
            
            try:
                response = auth.session.get(url, headers=headers, params=params, verify=False, timeout=15)
                
                print(f"🌐 V2 Response: Status {response.status_code}")
                
                if response.ok:
                    data = response.json()
                    print(f"✅ V2 SUCCESS! Got invoice data")
                    
                    # Check for invoices
                    invoices = data.get('invoices', [])
                    scheduled = data.get('scheduledPayments', [])
                    
                    print(f"📄 Found {len(invoices)} invoices, {len(scheduled)} scheduled payments")
                    
                    # Calculate past due amount using old working logic
                    amount_past_due = 0.0
                    unpaid_invoices = []
                    
                    for invoice in invoices:
                        amount = float(invoice.get('amount', 0))
                        status = invoice.get('status', '').upper()
                        
                        if status == 'UNPAID':
                            amount_past_due += amount
                            unpaid_invoices.append({
                                'id': invoice.get('id'),
                                'amount': amount,
                                'dueDate': invoice.get('dueDate'),
                                'description': invoice.get('description', '')
                            })
                    
                    print(f"💰 Calculated past due amount: ${amount_past_due:.2f}")
                    print(f"📋 Unpaid invoices: {len(unpaid_invoices)}")
                    
                    if unpaid_invoices:
                        for inv in unpaid_invoices:
                            print(f"  - Invoice {inv['id']}: ${inv['amount']:.2f} due {inv['dueDate']}")
                    
                    # Save detailed response for analysis
                    filename = f"v2_response_{agreement_id}.json"
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"💾 Saved V2 response to {filename}")
                    
                else:
                    print(f"❌ V2 FAILED: Status {response.status_code}")
                    print(f"Response: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"❌ V2 Exception: {e}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_old_v2_system()