#!/usr/bin/env python3
"""
Add agreement information for all members to the master contact list
Pull detailed agreement data for each of the 514 members
"""

import requests
import csv
import json
import time
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MemberAgreementEnhancer:
    def __init__(self):
        self.session = requests.Session()
        self.af_token = None
        self.base_url = "https://clubhub-ios-api.anytimefitness.com"
        
    def authenticate(self):
        """Authenticate with ClubHub using working credentials"""
        print("🔐 Authenticating with ClubHub...")
        
        login_url = f"{self.base_url}/api/login"
        
        login_data = {
            "username": "mayo.jeremy2212@gmail.com",
            "password": "SruLEqp464_GLrF"
        }
        
        headers = {
            'Content-Type': 'application/json',
            'API-version': '1',
            'Accept': 'application/json',
            'User-Agent': 'ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'br;q=1.0, gzip;q=0.9, deflate;q=0.8'
        }
        
        try:
            response = self.session.post(login_url, json=login_data, headers=headers, verify=False)
            
            if response.status_code == 200:
                auth_data = response.json()
                access_token = auth_data.get('accessToken')
                
                if access_token:
                    # Update session headers with the access token
                    self.session.headers.update({
                        'Authorization': f'Bearer {access_token}',
                        **headers
                    })
                    print("✅ ClubHub authentication successful!")
                    print(f"✅ Access token extracted: {access_token[:20]}...")
                    return True
                else:
                    print("❌ No access token found in auth response")
                    return False
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_member_agreements(self, member_id):
        """Get agreement information for a specific member using documented endpoints"""
        # Use the exact endpoints from all_api_endpoints.json
        agreement_endpoints = [
            f"/api/members/{member_id}/agreement",          # Current agreement
            f"/api/members/{member_id}/agreementHistory",   # Agreement history
            f"/api/members/{member_id}/agreementTokenQuery" # Agreement tokens
        ]
        
        all_agreement_data = {}
        
        for endpoint in agreement_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = self.session.get(url, verify=False, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        endpoint_name = endpoint.split('/')[-1]  # agreement, agreementHistory, etc.
                        all_agreement_data[endpoint_name] = data
                        print(f"    ✅ Found {endpoint_name} data")
                elif response.status_code == 404:
                    continue  # This endpoint doesn't have data for this member
                else:
                    print(f"    ⚠️ {endpoint}: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ Error on {endpoint}: {e}")
                continue
        
        if all_agreement_data:
            print(f"    ✅ Found agreement data: {list(all_agreement_data.keys())}")
            return all_agreement_data
        else:
            print(f"    ❌ No agreement data found for member {member_id}")
            return None
    
    def enhance_members_with_agreements(self, input_csv_file, output_csv_file):
        """Read the master contact list and add agreement data for members"""
        print(f"📋 Reading contact list from {input_csv_file}...")
        
        # Read the existing CSV
        contacts = []
        with open(input_csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            contacts = list(reader)
        
        print(f"📊 Loaded {len(contacts)} total contacts")
        
        # Filter to only members (not prospects)
        members = [c for c in contacts if c.get('prospect', '').lower() == 'false']
        prospects = [c for c in contacts if c.get('prospect', '').lower() == 'true']
        
        print(f"📊 Found {len(members)} members and {len(prospects)} prospects")
        
        if not members:
            print("❌ No members found to enhance with agreements")
            return
        
        print(f"🔍 Fetching agreement data for {len(members)} members...")
        
        enhanced_members = []
        
        for i, member in enumerate(members, 1):
            member_id = member.get('id')
            member_name = f"{member.get('firstName', '')} {member.get('lastName', '')}"
            
            print(f"  📄 {i}/{len(members)}: {member_name} (ID: {member_id})")
            
            if not member_id:
                print(f"    ⚠️ No member ID found, skipping")
                enhanced_members.append(member)
                continue
            
            # Get agreement data
            agreements = self.get_member_agreements(member_id)
            
            # Create enhanced member record
            enhanced_member = member.copy()
            
            if agreements:
                # Flatten agreement data from multiple endpoints into the member record
                for endpoint_name, endpoint_data in agreements.items():
                    if isinstance(endpoint_data, list):
                        # Handle array responses (like agreementHistory)
                        for j, agreement in enumerate(endpoint_data):
                            if isinstance(agreement, dict):
                                for key, value in agreement.items():
                                    enhanced_key = f"{endpoint_name}_{j+1}_{key}" if len(endpoint_data) > 1 else f"{endpoint_name}_{key}"
                                    enhanced_member[enhanced_key] = str(value) if value is not None else ''
                        
                        enhanced_member[f'{endpoint_name}_count'] = str(len(endpoint_data))
                        
                    elif isinstance(endpoint_data, dict):
                        # Handle object responses (like agreement)
                        for key, value in endpoint_data.items():
                            enhanced_key = f"{endpoint_name}_{key}"
                            enhanced_member[enhanced_key] = str(value) if value is not None else ''
                
                enhanced_member['agreements_found'] = 'Yes'
                enhanced_member['agreement_endpoints_found'] = ','.join(agreements.keys())
            else:
                enhanced_member['agreements_found'] = 'No'
                enhanced_member['agreement_endpoints_found'] = ''
            
            enhanced_members.append(enhanced_member)
            
            # Rate limiting
            time.sleep(0.1)
            
            # Progress update every 50 members
            if i % 50 == 0:
                print(f"    📊 Progress: {i}/{len(members)} members processed...")
        
        # Combine enhanced members with prospects
        all_enhanced_contacts = enhanced_members + prospects
        
        print(f"💾 Saving enhanced contact list to {output_csv_file}...")
        
        # Get all possible fieldnames from enhanced data
        all_fieldnames = set()
        for contact in all_enhanced_contacts:
            all_fieldnames.update(contact.keys())
        
        fieldnames = sorted(list(all_fieldnames))
        
        # Write enhanced CSV
        with open(output_csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for contact in all_enhanced_contacts:
                # Ensure all fields are present
                row = {}
                for field in fieldnames:
                    row[field] = contact.get(field, '')
                writer.writerow(row)
        
        print(f"✅ Enhanced contact list saved!")
        print(f"📊 Total contacts: {len(all_enhanced_contacts)}")
        print(f"📊 Members with agreements: {len([m for m in enhanced_members if m.get('agreements_found') == 'Yes'])}")
        print(f"📊 Members without agreements: {len([m for m in enhanced_members if m.get('agreements_found') == 'No'])}")
        print(f"📊 Total fields: {len(fieldnames)}")

def main():
    enhancer = MemberAgreementEnhancer()
    
    if not enhancer.authenticate():
        print("❌ Authentication failed, cannot proceed")
        return
    
    # Use the latest master contact list
    input_file = "master_contact_list_club1156_20250722_171618.csv"
    output_file = f"master_contact_list_with_agreements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    enhancer.enhance_members_with_agreements(input_file, output_file)
    
    print(f"\n🎉 Agreement enhancement complete!")
    print(f"📁 Enhanced file: {output_file}")

if __name__ == "__main__":
    main()
