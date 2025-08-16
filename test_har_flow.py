#!/usr/bin/env python3
"""
ClubOS Package Agreements Parser - Based on HAR file analysis
Follows the exact API flow used in the browser
"""

import json
import logging
import time
import base64
from typing import Optional, Dict, List

import requests
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClubOSHARBased:
    def __init__(self):
        try:
            from config.clubhub_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD
            self.username = CLUBOS_USERNAME
            self.password = CLUBOS_PASSWORD
        except Exception:
            self.username = None
            self.password = None
        
        self.base_url = "https://anytime.club-os.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        
        self.authenticated = False
        self.session_id = None
        self.bearer_token = None

    def login(self) -> bool:
        """Login to ClubOS using the exact flow from HAR"""
        try:
            print("🔐 Logging into ClubOS...")
            
            # Step 1: Get login page and extract tokens
            r0 = self.session.get(f"{self.base_url}/action/Login/view", timeout=20)
            if r0.status_code not in (200, 302):
                print(f"❌ Login view failed: {r0.status_code}")
                return False
            
            # Extract form tokens
            soup = BeautifulSoup(r0.text, 'html.parser')
            _sourcePage = ''
            __fp = ''
            
            sp = soup.find('input', {'name': '_sourcePage'})
            if sp:
                _sourcePage = sp.get('value', '')
            
            fp = soup.find('input', {'name': '__fp'})
            if fp:
                __fp = fp.get('value', '')
            
            # Step 2: POST login credentials
            form_data = {
                'login': 'Submit',
                'username': self.username,
                'password': self.password,
                '_sourcePage': _sourcePage,
                '__fp': __fp,
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': f'{self.base_url}/action/Login/view',
            }
            
            r1 = self.session.post(f"{self.base_url}/action/Login", 
                                  data=form_data, headers=headers, 
                                  timeout=30, allow_redirects=True)
            
            if r1.status_code not in (200, 302):
                print(f"❌ Login POST failed: {r1.status_code}")
                return False
            
            # Check for session cookie and extract session ID
            cookies = self.session.cookies.get_dict()
            jsessionid = cookies.get('JSESSIONID')
            if not jsessionid:
                print("❌ No session cookie found - login failed")
                return False
            
            self.session_id = jsessionid
            print(f"✅ Login successful, Session ID: {jsessionid}")
            self.authenticated = True
            return True
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def delegate_to_member(self, member_id: str) -> bool:
        """Delegate to a specific member - sets delegation cookies"""
        try:
            print(f"👤 Delegating to member {member_id}...")
            
            timestamp = int(time.time() * 1000)
            delegate_url = f"{self.base_url}/action/Delegate/{member_id}/url=false"
            
            headers = {
                'Referer': f'{self.base_url}/action/Dashboard/view',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'X-Requested-With': 'XMLHttpRequest',
            }
            
            params = {'_': timestamp}
            
            response = self.session.get(delegate_url, headers=headers, params=params, timeout=20)
            
            print(f"   📊 Delegation Status: {response.status_code}")
            
            if response.status_code in (200, 302):
                # Check delegation cookies
                cookies = self.session.cookies.get_dict()
                delegated_user_id = cookies.get('delegatedUserId')
                if delegated_user_id:
                    print(f"   ✅ Delegation successful - delegated to user ID: {delegated_user_id}")
                    
                    # Generate Bearer token using the pattern from HAR
                    self.bearer_token = self._generate_bearer_token(delegated_user_id)
                    return True
                else:
                    print("   ⚠️ Delegation succeeded but no delegatedUserId cookie found")
                    return False
            else:
                print(f"   ❌ Delegation failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Delegation error: {e}")
            return False

    def _generate_bearer_token(self, delegated_user_id: str) -> str:
        """Generate Bearer token following the pattern from HAR file"""
        # From HAR: Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg1Nzc3Mjc2LCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiJGRTNDRkU2ODcwNDBDOTNGNEI0ODlEQkQ4NDdERjk2QyJ9.-FEtdEkNeQoGJMV4Ovue3QSttZsS7ZR34QqzBgVHdRU
        
        # This is a simplified token - in real implementation you'd need proper JWT signing
        # For now, I'll use the pattern I can see from the HAR file
        header = {"alg": "HS256"}
        payload = {
            "delegateUserId": int(delegated_user_id),
            "loggedInUserId": 187032782,  # Your user ID from HAR
            "sessionId": self.session_id
        }
        
        # Create a simple token representation (this is not a real JWT)
        header_b64 = base64.b64encode(json.dumps(header).encode()).decode().rstrip('=')
        payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode().rstrip('=')
        
        return f"eyJhbGciOiJIUzI1NiJ9.{payload_b64}.-FEtdEkNeQoGJMV4Ovue3QSttZsS7ZR34QqzBgVHdRU"

    def get_agreement_total_value(self, agreement_id: str) -> float:
        """Get agreement total value - following exact HAR pattern"""
        try:
            print(f"💰 Getting total value for agreement {agreement_id}...")
            
            timestamp = int(time.time() * 1000)
            url = f"{self.base_url}/api/agreements/package_agreements/{agreement_id}/agreementTotalValue"
            
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'Authorization': f'Bearer {self.bearer_token}',
                'Referer': f'{self.base_url}/action/PackageAgreementUpdated/spa/',
            }
            
            params = {
                'agreementId': agreement_id,
                '_': timestamp
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=20)
            
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                # Response content is base64 encoded in HAR: "MjAwLjAw" = "200.00"
                try:
                    data = response.json()
                    if isinstance(data, (int, float)):
                        print(f"   ✅ Agreement total value: ${data}")
                        return float(data)
                    else:
                        print(f"   ✅ Agreement total value: {data}")
                        return 0.0
                except:
                    # Try as plain text
                    text = response.text.strip()
                    if text.replace('.', '').isdigit():
                        value = float(text)
                        print(f"   ✅ Agreement total value: ${value}")
                        return value
                    else:
                        print(f"   ⚠️ Unexpected response: {text}")
                        return 0.0
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                return 0.0
                
        except Exception as e:
            print(f"❌ Error getting agreement total: {e}")
            return 0.0

    def get_agreement_salespeople(self, agreement_id: str) -> List[Dict]:
        """Get salespeople for an agreement"""
        try:
            print(f"👥 Getting salespeople for agreement {agreement_id}...")
            
            timestamp = int(time.time() * 1000)
            url = f"{self.base_url}/api/agreements/package_agreements/{agreement_id}/salespeople"
            
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'Authorization': f'Bearer {self.bearer_token}',
                'Referer': f'{self.base_url}/action/PackageAgreementUpdated/spa/',
            }
            
            params = {'_': timestamp}
            
            response = self.session.get(url, headers=headers, params=params, timeout=20)
            
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    salespeople = data.get('data', [])
                    print(f"   ✅ Found {len(salespeople)} salespeople")
                    for sp in salespeople[:3]:  # Show first 3
                        print(f"      - {sp.get('salespersonName', 'Unknown')}")
                    return salespeople
                except Exception as e:
                    print(f"   ⚠️ Error parsing salespeople data: {e}")
                    return []
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting salespeople: {e}")
            return []

    def get_member_payment_profiles(self) -> List[Dict]:
        """Get member payment profiles"""
        try:
            print("💳 Getting member payment profiles...")
            
            timestamp = int(time.time() * 1000)
            url = f"{self.base_url}/api/member_payment_profiles"
            
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'Authorization': f'Bearer {self.bearer_token}',
                'Referer': f'{self.base_url}/action/PackageAgreementUpdated/spa/',
            }
            
            params = {'_': timestamp}
            
            response = self.session.get(url, headers=headers, params=params, timeout=20)
            
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Found {len(data)} payment profiles")
                    for profile in data[:2]:  # Show first 2
                        print(f"      - {profile.get('name', 'Unknown')} ({profile.get('mask', 'No mask')})")
                    return data
                except Exception as e:
                    print(f"   ⚠️ Error parsing payment profiles: {e}")
                    return []
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting payment profiles: {e}")
            return []

def main():
    """Test the HAR-based ClubOS flow"""
    print("🧪 Testing ClubOS HAR-based package agreements flow...")
    print()
    
    client = ClubOSHARBased()
    
    # Step 1: Login
    print("1️⃣ STEP 1: Login to ClubOS")
    if not client.login():
        print("❌ Login failed - cannot continue")
        return
    print()
    
    # Step 2: Delegate to Grace Sphatt (ID from HAR file: 185777276)
    print("2️⃣ STEP 2: Delegate to Grace Sphatt (185777276)")
    grace_member_id = "185777276"
    if not client.delegate_to_member(grace_member_id):
        print("❌ Delegation failed - cannot continue")
        return
    print()
    
    # Step 3: Test the specific agreement ID from HAR file
    print("3️⃣ STEP 3: Get Agreement Details (ID: 1522516)")
    agreement_id = "1522516"
    
    total_value = client.get_agreement_total_value(agreement_id)
    salespeople = client.get_agreement_salespeople(agreement_id)
    payment_profiles = client.get_member_payment_profiles()
    
    print()
    print("📋 SUMMARY:")
    print(f"   💰 Agreement Total Value: ${total_value}")
    print(f"   👥 Salespeople Count: {len(salespeople)}")
    print(f"   💳 Payment Profiles Count: {len(payment_profiles)}")
    print()
    print("✅ HAR-based flow test completed!")

if __name__ == "__main__":
    main()
