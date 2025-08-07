import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_api import ClubOSTrainingPackageAPI
import requests
import time
import re
import json

def get_clubservices_training_data(member_id):
    """Get training data using ClubServicesNew endpoint like the HAR files show"""
    print(f"🏋️ Getting training data via ClubServices for member ID: {member_id}")
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ ClubOS authentication failed")
        return None
    
    try:
        # Step 1: Navigate to PackageAgreementUpdated page (this is where the Bearer token is generated)
        print("🔄 Loading PackageAgreementUpdated page...")
        package_agreement_url = f"{api.base_url}/action/PackageAgreementUpdated/"
        
        package_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Referer': f'{api.base_url}/action/Dashboard/view'
        }
        
        package_response = api.session.get(package_agreement_url, headers=package_headers)
        
        if package_response.status_code != 200:
            print(f"❌ PackageAgreementUpdated page failed: {package_response.status_code}")
            return None
            
        print("✅ PackageAgreementUpdated page loaded")
        
        # Step 2: Extract the access token from the PackageAgreementUpdated page
        page_html = package_response.text
        token_patterns = [
            r'var ACCESS_TOKEN = ["\']([^"\']+)["\']',
            r'ACCESS_TOKEN\s*:\s*["\']([^"\']+)["\']',
            r'window\.ACCESS_TOKEN\s*=\s*["\']([^"\']+)["\']',
            r'accessToken\s*:\s*["\']([^"\']+)["\']',
            r'["\']?access_token["\']?\s*:\s*["\']([^"\']+)["\']',
            r'token\s*:\s*["\']([^"\']+)["\']'
        ]
        
        access_token = None
        for pattern in token_patterns:
            token_match = re.search(pattern, page_html, re.IGNORECASE)
            if token_match:
                access_token = token_match.group(1)
                print(f"✅ Found ACCESS_TOKEN using pattern: {pattern}")
                break
        
        if not access_token:
            print("❌ Could not extract ACCESS_TOKEN from PackageAgreementUpdated page")
            return None
        
        # Step 3: Set delegation to the target member
        print(f"🔄 Setting delegation to member {member_id}...")
        delegation_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': package_agreement_url
        }
        
        delegate_url = f"{api.base_url}/action/Delegate/{member_id}/url=false"
        delegate_params = {'_': int(time.time() * 1000)}
        
        delegate_response = api.session.get(delegate_url, headers=delegation_headers, params=delegate_params)
        
        if delegate_response.status_code != 200:
            print(f"❌ Delegation failed: {delegate_response.status_code}")
            return None
            
        print("✅ Delegation successful")
        
        # Step 4: Get package agreements list using the ClubServices API pattern
        print("🔍 Getting package agreements list...")
        
        api_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Authorization': f'Bearer {access_token}',
            'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Referer': package_agreement_url
        }
        
        # Call the package agreements list API (this is what ClubServicesNew uses)
        agreements_url = f"{api.base_url}/api/agreements/package_agreements/list"
        timestamp = int(time.time() * 1000)
        
        agreements_response = api.session.get(agreements_url, headers=api_headers, timeout=10)
        
        if agreements_response.status_code != 200:
            print(f"❌ Package agreements API failed: {agreements_response.status_code}")
            print(f"Response: {agreements_response.text}")
            return None
            
        agreements_data = agreements_response.json()
        print(f"✅ Got package agreements data: {len(agreements_data) if isinstance(agreements_data, list) else 'Got data'}")
        
        if not agreements_data or (isinstance(agreements_data, list) and len(agreements_data) == 0):
            print(f"❌ No package agreements found for member {member_id}")
            return None
            
        # Step 5: Get invoices/billing data for each agreement
        print("💰 Getting billing/invoice data...")
        
        total_past_due = 0.0
        training_data = {
            'member_id': member_id,
            'agreements': [],
            'total_past_due': 0.0,
            'status': 'unknown'
        }
        
        for agreement in (agreements_data if isinstance(agreements_data, list) else [agreements_data]):
            agreement_id = agreement.get('id')
            agreement_name = agreement.get('packageName', 'Unknown Package')
            agreement_status = agreement.get('agreementStatus', 'Unknown')
            
            print(f"📋 Processing agreement: {agreement_name} (ID: {agreement_id}, Status: {agreement_status})")
            
            if agreement_id:
                # Get invoices for this agreement (this is how ClubServices gets billing info)
                invoices_url = f"{api.base_url}/api/agreements/package_agreements/invoices"
                
                # The invoices endpoint expects a POST with agreement data
                invoice_payload = {
                    "agreementId": agreement_id,
                    "memberId": member_id
                }
                
                invoice_headers = api_headers.copy()
                invoice_headers['Content-Type'] = 'application/json'
                
                invoices_response = api.session.post(
                    invoices_url, 
                    headers=invoice_headers, 
                    json=invoice_payload,
                    timeout=10
                )
                
                if invoices_response.status_code == 200:
                    invoices_data = invoices_response.json()
                    print(f"✅ Got invoices data for agreement {agreement_id}")
                    
                    # Parse invoice data for past due amounts
                    past_due_amount = 0.0
                    
                    if isinstance(invoices_data, list):
                        for invoice in invoices_data:
                            status = invoice.get('status', '').lower()
                            amount = float(invoice.get('amount', 0))
                            due_date = invoice.get('dueDate', 'Unknown')
                            
                            if 'past' in status or 'overdue' in status or 'unpaid' in status:
                                past_due_amount += amount
                                print(f"   💸 Past due: ${amount:.2f} (due: {due_date})")
                    
                    agreement_data = {
                        'id': agreement_id,
                        'name': agreement_name,
                        'status': agreement_status,
                        'past_due_amount': past_due_amount,
                        'invoices': invoices_data
                    }
                    
                    training_data['agreements'].append(agreement_data)
                    total_past_due += past_due_amount
                    
                else:
                    print(f"❌ Failed to get invoices for agreement {agreement_id}: {invoices_response.status_code}")
        
        training_data['total_past_due'] = total_past_due
        training_data['status'] = 'Past Due' if total_past_due > 0 else 'Current'
        
        print(f"\n💰 TRAINING DATA SUMMARY:")
        print(f"   Member ID: {member_id}")
        print(f"   Agreements found: {len(training_data['agreements'])}")
        print(f"   Total past due: ${total_past_due:.2f}")
        print(f"   Status: {training_data['status']}")
        
        return training_data
        
    except Exception as e:
        print(f"❌ Error getting ClubServices training data: {e}")
        return None

def test_dennis_clubservices():
    """Test Dennis using the ClubServices approach with multiple ID attempts"""
    print("🧪 TESTING DENNIS VIA CLUBSERVICES WITH MULTIPLE IDS")
    print("=" * 60)
    
    # Try all possible Dennis IDs from CSV and variations
    dennis_id_variations = [
        ("ClubHub ID", "65828815"),
        ("CSV agreement_agreementID", "96530079"),
        ("CSV userId", "31489560"),
        ("CSV agreementHistory_memberId", "65828815"),  # Same as ClubHub but try anyway
        ("Jordan's working ClubOS ID (test)", "160402199"),  # Test with known working ID
    ]
    
    for id_description, test_id in dennis_id_variations:
        print(f"\n🔍 TESTING {id_description}: {test_id}")
        print("-" * 40)
        
        training_data = get_clubservices_training_data(test_id)
        
        if training_data and training_data['agreements']:
            print(f"\n🎉 FOUND TRAINING DATA WITH {id_description}!")
            print(f"Past due amount: ${training_data['total_past_due']:.2f}")
            
            for agreement in training_data['agreements']:
                print(f"\n📋 {agreement['name']}:")
                print(f"   Status: {agreement['status']}")
                print(f"   Past due: ${agreement['past_due_amount']:.2f}")
                
            return training_data  # Found it, return the data
            
        else:
            print(f"❌ No training data found with {id_description}")
    
    print(f"\n❌ Could not find Dennis's training data with any ID variation")
    return None

if __name__ == "__main__":
    test_dennis_clubservices()
