import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_api import ClubOSTrainingPackageAPI
import requests
import time

def get_dennis_detailed_payment_info():
    """Get Dennis's detailed payment information from ClubOS API"""
    print("💰 Getting Dennis's detailed payment information from ClubOS...")
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ ClubOS authentication failed")
        return
    
    dennis_id = "65828815"  # Dennis's ClubHub ID
    print(f"🔍 Looking up payment details for Dennis (ID: {dennis_id})")
    
    try:
        # Step 1: Set delegation to Dennis
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
            'Referer': f'{api.base_url}/action/Dashboard/view'
        }
        
        delegate_url = f"{api.base_url}/action/Delegate/{dennis_id}/url=false"
        delegate_params = {'_': int(time.time() * 1000)}
        
        print("🔄 Setting delegation to Dennis...")
        delegate_response = api.session.get(delegate_url, headers=delegation_headers, params=delegate_params)
        
        if delegate_response.status_code != 200:
            print(f"❌ Delegation failed: {delegate_response.status_code}")
            return
            
        print("✅ Delegation successful")
        
        # Step 2: Navigate to PackageAgreementUpdated/spa/ to get the delegated token
        package_agreement_url = f"{api.base_url}/action/PackageAgreementUpdated/spa/"
        package_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Referer': f'{api.base_url}/action/Dashboard/view'
        }
        
        print("🔄 Getting delegated token...")
        package_response = api.session.get(package_agreement_url, headers=package_headers)
        
        if package_response.status_code != 200:
            print(f"❌ Package agreement page failed: {package_response.status_code}")
            return
        
        # Extract the delegated ACCESS_TOKEN from the page's JavaScript
        import re
        page_html = package_response.text
        token_match = re.search(r'var ACCESS_TOKEN = "([^"]+)";', page_html)
        
        if not token_match:
            print("❌ Could not extract delegated token")
            return
            
        delegated_token = token_match.group(1)
        print("✅ Got delegated token")
        
        # Step 3: Look for Dennis's agreements and billing data
        timestamp = int(time.time() * 1000)
        
        api_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Authorization': f'Bearer {delegated_token}',
            'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'{api.base_url}/action/PackageAgreementUpdated/spa/'
        }
        
        # Try to find agreements for Dennis
        print("🔍 Searching for Dennis's agreements...")
        
        discovery_endpoints = [
            f"/api/agreements/package_agreements/list?memberId={dennis_id}",
            f"/api/agreements/package_agreements/active?memberId={dennis_id}",
            f"/api/members/{dennis_id}/active_agreements",
            f"/api/agreements/package_agreements?memberId={dennis_id}",
            f"/api/agreements?memberId={dennis_id}",
            f"/api/members/{dennis_id}/agreements"
        ]
        
        agreements_found = []
        
        for endpoint in discovery_endpoints:
            try:
                url = f"{api.base_url}{endpoint}"
                params = {'_': timestamp}
                
                print(f"   🔍 Trying: {endpoint}")
                response = api.session.get(url, headers=api_headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ {endpoint}: {len(data) if isinstance(data, list) else 'Got data'}")
                    
                    if isinstance(data, list) and data:
                        agreements_found.extend(data)
                    elif isinstance(data, dict) and data:
                        agreements_found.append(data)
                        
                else:
                    print(f"   ❌ {endpoint}: {response.status_code}")
                    
            except Exception as e:
                print(f"   ⚠️ {endpoint}: Error - {str(e)}")
        
        if not agreements_found:
            print("❌ No agreements found for Dennis")
            return
            
        print(f"\n📋 Found {len(agreements_found)} agreement(s) for Dennis:")
        
        total_past_due = 0.0
        
        for i, agreement in enumerate(agreements_found):
            print(f"\n📄 Agreement {i+1}:")
            print(f"   ID: {agreement.get('id')}")
            print(f"   Status: {agreement.get('agreementStatus')}")
            print(f"   Package: {agreement.get('packageName', agreement.get('package', {}).get('name', 'Unknown'))}")
            
            # Get billing status for this agreement
            agreement_id = agreement.get('id')
            if agreement_id:
                try:
                    billing_url = f"{api.base_url}/api/agreements/package_agreements/{agreement_id}/billing_status"
                    billing_params = {'_': timestamp + i}
                    
                    print(f"   🔍 Getting billing status...")
                    billing_response = api.session.get(billing_url, headers=api_headers, params=billing_params, timeout=10)
                    
                    if billing_response.status_code == 200:
                        billing_data = billing_response.json()
                        
                        print(f"   💰 Billing Data:")
                        print(f"      Current due: {billing_data.get('current', [])}")
                        
                        past_due_items = billing_data.get('past', [])
                        if past_due_items:
                            print(f"      💸 Past due items: {len(past_due_items)}")
                            for item in past_due_items:
                                amount = float(item.get('amount', 0))
                                total_past_due += amount
                                print(f"         - ${amount:.2f} due {item.get('dueDate', 'Unknown date')}")
                        else:
                            print(f"      ✅ No past due items")
                            
                        # Check for other billing info
                        print(f"      📊 Full billing data: {billing_data}")
                        
                    else:
                        print(f"   ❌ Billing status failed: {billing_response.status_code}")
                        
                except Exception as e:
                    print(f"   ⚠️ Error getting billing status: {str(e)}")
        
        print(f"\n💰 DENNIS'S PAYMENT SUMMARY:")
        print(f"   Total Past Due Amount: ${total_past_due:.2f}")
        if total_past_due > 0:
            print(f"   Status: PAST DUE")
        else:
            print(f"   Status: CURRENT or NO ACTIVE TRAINING")
            
    except Exception as e:
        print(f"❌ Error getting Dennis's payment info: {str(e)}")

if __name__ == "__main__":
    get_dennis_detailed_payment_info()
