#!/usr/bin/env python3
"""
Quick test to check if Agreement 1522516 still exists and what its current state is
"""

import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

def quick_auth_and_test():
    session = requests.Session()
    base_url = "https://anytime.club-os.com"
    
    # Quick authentication
    print("🔐 Quick authentication...")
    
    # Get login page
    login_response = session.get(f"{base_url}/action/Login/view")
    soup = BeautifulSoup(login_response.text, 'html.parser')
    
    # Extract form fields
    form_data = {}
    for hidden_input in soup.find_all('input', type='hidden'):
        name = hidden_input.get('name')
        value = hidden_input.get('value', '')
        if name:
            form_data[name] = value
    
    # Login
    login_data = {
        'login': 'Submit',
        'username': 'j.mayo', 
        'password': 'j@SD4fjhANK5WNA',
        '_sourcePage': form_data['_sourcePage'],
        '__fp': form_data['__fp']
    }
    
    auth_response = session.post(f"{base_url}/action/Login", data=login_data, allow_redirects=True)
    
    if "Dashboard" not in auth_response.url:
        print("❌ Auth failed")
        return
    
    # Get tokens
    api_token = session.cookies.get('apiV3AccessToken')
    if not api_token:
        print("❌ No API token")
        return
    
    print("✅ Authenticated")
    
    # Set delegation to Leisa
    print("🎭 Setting delegation to Leisa...")
    delegate_url = f"{base_url}/action/Delegate/185777276/url=false"
    delegate_params = {'_': int(datetime.now().timestamp() * 1000)}
    delegate_response = session.get(delegate_url, params=delegate_params)
    print(f"Delegation: {delegate_response.status_code}")
    
    # Navigate to packages page
    print("📦 Loading packages page...")
    package_url = f"{base_url}/action/PackageAgreementUpdated/spa/"
    package_response = session.get(package_url)
    print(f"Packages page: {package_response.status_code}")
    
    # Test agreement endpoints
    api_headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': '*/*',
        'Referer': f'{base_url}/action/PackageAgreementUpdated/spa/',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    timestamp = str(int(datetime.now().timestamp() * 1000))
    
    test_endpoints = [
        f"/api/agreements/package_agreements/1522516",
        f"/api/agreements/package_agreements/1522516?_={timestamp}",
        f"/api/agreements/package_agreements/1522516/billing_status?_={timestamp}",
        f"/api/agreements/package_agreements/V2/1522516?include=invoices&include=scheduledPayments&_={timestamp}",
    ]
    
    print("\n🔍 Testing agreement endpoints...")
    for endpoint in test_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = session.get(url, headers=api_headers, timeout=10)
            print(f"  {endpoint}")
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        agreement_id = data.get('id', 'N/A')
                        name = data.get('name', 'N/A')
                        status = data.get('agreementStatus', 'N/A')
                        member_id = data.get('memberId', 'N/A')
                        print(f"    ✅ Agreement {agreement_id}: {name} (Status: {status}, Member: {member_id})")
                        
                        # Check for billing data
                        if 'invoices' in data:
                            invoices = data.get('invoices', [])
                            print(f"    💰 Invoices: {len(invoices)}")
                        if 'scheduledPayments' in data:
                            payments = data.get('scheduledPayments', [])
                            print(f"    📅 Scheduled Payments: {len(payments)}")
                    else:
                        print(f"    ✅ Response: {str(data)[:100]}")
                except:
                    print(f"    ✅ Text response: {response.text[:200]}")
            else:
                print(f"    ❌ Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"    ❌ Exception: {e}")

if __name__ == "__main__":
    quick_auth_and_test()
