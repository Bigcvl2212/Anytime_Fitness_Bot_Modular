import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_api import ClubOSTrainingPackageAPI

def get_member_past_due_amount(member_id):
    """Get the actual past due amount for a member from ClubOS"""
    print(f"💰 Getting past due amount for member ID: {member_id}")
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ ClubOS authentication failed")
        return None
    
    try:
        # Step 1: Set delegation to target member
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
        
        import time
        from datetime import datetime
        
        delegate_url = f"{api.base_url}/action/Delegate/{member_id}/url=false"
        delegate_params = {'_': int(datetime.now().timestamp() * 1000)}
        
        delegate_response = api.session.get(delegate_url, headers=delegation_headers, params=delegate_params)
        
        if delegate_response.status_code != 200:
            print(f"❌ Delegation failed: {delegate_response.status_code}")
            return None
            
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
        
        package_response = api.session.get(package_agreement_url, headers=package_headers)
        
        if package_response.status_code != 200:
            print(f"❌ Package agreement page failed: {package_response.status_code}")
            return None
        
        # Extract the delegated ACCESS_TOKEN from the page's JavaScript
        import re
        page_html = package_response.text
        token_match = re.search(r'var ACCESS_TOKEN = "([^"]+)";', page_html)
        
        if not token_match:
            print("❌ Could not extract delegated token")
            return None
            
        delegated_token = token_match.group(1)
        print("✅ Got delegated token")
        
        # Step 3: Call billing_status API with the delegated token
        timestamp = int(time.time() * 1000)
        
        # First, discover active agreements for this member
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
        
        # Try to find active agreements
        discovery_endpoints = [
            f"/api/agreements/package_agreements/list?memberId={member_id}",
            f"/api/agreements/package_agreements/active?memberId={member_id}",
            f"/api/members/{member_id}/active_agreements",
            f"/api/agreements/package_agreements?memberId={member_id}",
        ]
        
        total_past_due = 0.0
        agreements_found = 0
        
        for endpoint in discovery_endpoints:
            try:
                url = f"{api.base_url}{endpoint}"
                params = {'_': timestamp}
                
                response = api.session.get(url, headers=api_headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and data:
                        print(f"✅ Found {len(data)} agreements via {endpoint}")
                        
                        for agreement in data:
                            agreements_found += 1
                            agreement_id = agreement.get('id')
                            
                            if agreement_id:
                                # Get billing status for this agreement
                                billing_url = f"{api.base_url}/api/agreements/package_agreements/{agreement_id}/billing_status"
                                billing_params = {'_': timestamp + agreements_found}
                                
                                billing_response = api.session.get(billing_url, headers=api_headers, params=billing_params, timeout=10)
                                
                                if billing_response.status_code == 200:
                                    billing_data = billing_response.json()
                                    
                                    # Check for past due items
                                    past_due_items = billing_data.get('past', [])
                                    
                                    if past_due_items:
                                        print(f"📋 Agreement {agreement_id} has {len(past_due_items)} past due items:")
                                        for item in past_due_items:
                                            amount = float(item.get('amount', 0))
                                            due_date = item.get('dueDate', 'Unknown')
                                            total_past_due += amount
                                            print(f"   💸 ${amount:.2f} due on {due_date}")
                                    else:
                                        print(f"✅ Agreement {agreement_id} has no past due amounts")
                                        
                                    # Also check current due items
                                    current_due_items = billing_data.get('current', [])
                                    if current_due_items:
                                        print(f"📋 Agreement {agreement_id} has {len(current_due_items)} current due items:")
                                        for item in current_due_items:
                                            amount = float(item.get('amount', 0))
                                            due_date = item.get('dueDate', 'Unknown')
                                            print(f"   💰 ${amount:.2f} due on {due_date}")
                                            
                        # Found agreements, break out of endpoint loop
                        break
                        
            except Exception as e:
                continue
        
        if agreements_found == 0:
            print("❌ No training agreements found for this member")
            return None
            
        print(f"\n💰 TOTAL PAST DUE AMOUNT: ${total_past_due:.2f}")
        return total_past_due
        
    except Exception as e:
        print(f"❌ Error getting past due amount: {e}")
        return None

def test_dennis_past_due():
    """Test getting Dennis's past due amount"""
    print("🧪 TESTING DENNIS'S PAST DUE AMOUNT")
    print("=" * 40)
    
    # Test with Dennis's ClubHub ID
    dennis_id = "65828815"
    past_due = get_member_past_due_amount(dennis_id)
    
    if past_due is not None:
        if past_due > 0:
            print(f"✅ Dennis owes: ${past_due:.2f}")
        else:
            print(f"✅ Dennis is current (no past due amount)")
    else:
        print(f"❌ Could not get Dennis's payment information")

if __name__ == "__main__":
    test_dennis_past_due()
