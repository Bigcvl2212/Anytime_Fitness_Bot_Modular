#!/usr/bin/env python3
"""
Debug script to see what actual fields the /members/all API returns
"""

import requests
import json
import base64

class APIFieldInspector:
    def __init__(self):
        self.base_url = "https://clubhub-ios-api.anytimefitness.com"
        self.session = requests.Session()
        self.username = "mayo.jeremy2212@gmail.com"
        self.password = "SruLEqp464_GLrF"
        
        self.headers = {
            'Content-Type': 'application/json',
            'API-version': '1',
            'Accept': 'application/json',
            'User-Agent': 'ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'br;q=1.0, gzip;q=0.9, deflate;q=0.8'
        }
    
    def authenticate(self):
        login_url = f"{self.base_url}/api/login"
        payload = {"username": self.username, "password": self.password}
        
        response = self.session.post(login_url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('accessToken')
            
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                **self.headers
            })
            
            print("✅ Authentication successful!")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    
    def inspect_members_all_fields(self):
        """Get a sample from /members/all and show what fields are actually available"""
        print("🔍 Inspecting /members/all endpoint...")
        
        members_all_url = f"{self.base_url}/api/clubs/1156/members/all"
        
        try:
            response = self.session.get(members_all_url, verify=False, timeout=30)
            if response.status_code == 200:
                members_data = response.json()
                if isinstance(members_data, list) and len(members_data) > 0:
                    print(f"📊 Found {len(members_data)} total members")
                    
                    # Analyze first 5 members to see field structure
                    print(f"\n🔍 ANALYZING FIELD STRUCTURE:")
                    print("="*60)
                    
                    for i, member in enumerate(members_data[:5], 1):
                        print(f"\n👤 MEMBER {i} FIELDS:")
                        print("-" * 30)
                        for key, value in member.items():
                            # Show value type and truncated sample
                            value_type = type(value).__name__
                            if isinstance(value, str):
                                sample = value[:50] + "..." if len(value) > 50 else value
                            elif isinstance(value, dict):
                                sample = f"Dict with keys: {list(value.keys())}"
                            elif isinstance(value, list):
                                sample = f"List with {len(value)} items"
                            else:
                                sample = str(value)
                            
                            print(f"  {key}: {value_type} = {sample}")
                    
                    # Get all unique field names across all members
                    all_fields = set()
                    for member in members_data[:100]:  # Check first 100 for performance
                        all_fields.update(member.keys())
                    
                    print(f"\n📋 ALL AVAILABLE FIELDS ({len(all_fields)} total):")
                    print("="*60)
                    sorted_fields = sorted(list(all_fields))
                    for i, field in enumerate(sorted_fields, 1):
                        print(f"{i:2d}. {field}")
                    
                    # Show sample member with all data
                    print(f"\n📝 COMPLETE SAMPLE MEMBER (non-deleted):")
                    print("="*60)
                    
                    # Find a non-deleted member
                    sample_member = None
                    for member in members_data:
                        if member.get('firstName') != 'DELETED':
                            sample_member = member
                            break
                    
                    if sample_member:
                        print(json.dumps(sample_member, indent=2, default=str))
                    else:
                        print("No non-deleted members found in sample")
                        
                else:
                    print("⚠️ Unexpected response format")
            else:
                print(f"❌ Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    inspector = APIFieldInspector()
    if inspector.authenticate():
        inspector.inspect_members_all_fields()

if __name__ == "__main__":
    main()
