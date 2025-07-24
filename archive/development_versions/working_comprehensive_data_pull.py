import requests
import json
import csv
import sqlite3
from datetime import datetime, timedelta
import os
import base64

class ClubOSDataPuller:
    """Pull comprehensive data from ClubOS API - has the full dataset"""
    
    def __init__(self):
        # Use the ClubHub API like the old script did
        self.base_url = "https://clubhub-ios-api.anytimefitness.com"
        self.access_token = None
        self.refresh_token = None
        self.af_api_token = None
        self.session = requests.Session()
        
        # Working credentials
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
        """Authenticate with ClubHub using working credentials"""
        print("🔐 Authenticating with ClubHub...")
        
        login_url = f"{self.base_url}/api/login"
        payload = {
            "username": self.username,
            "password": self.password
        }
        
        try:
            response = self.session.post(login_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('accessToken')
                self.refresh_token = data.get('refreshToken')
                
                # Update session headers
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    **self.headers
                })
                
                print("✅ ClubHub authentication successful!")
                
                # Decode JWT to get AF API token
                self._extract_af_token()
                return True
                
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def _extract_af_token(self):
        """Extract AF API token from JWT"""
        try:
            # Decode JWT payload (skip signature verification)
            token_parts = self.access_token.split('.')
            payload_encoded = token_parts[1]
            
            # Add padding if needed
            payload_encoded += '=' * (4 - len(payload_encoded) % 4)
            payload_decoded = base64.b64decode(payload_encoded)
            payload_data = json.loads(payload_decoded)
            
            self.af_api_token = payload_data.get('af_api_token')
            print(f"✅ AF API token extracted: {self.af_api_token[:20]}...")
            
        except Exception as e:
            print(f"⚠️ Could not extract AF API token: {e}")
    
    def get_prospects_and_members(self, club_id):
        """Get ALL prospects and members using the /all endpoint found in HAR analysis"""
        print(f"📋 Fetching ALL prospects and members for club {club_id}...")
        
        all_contacts = []
        
        # Use the /members/all endpoint that returned 10,216 records in HAR
        print(f"🎯 Using /members/all endpoint that got 10,216 records in HAR...")
        members_all_url = f"{self.base_url}/api/clubs/{club_id}/members/all"
        
        try:
            response = self.session.get(members_all_url, verify=False, timeout=30)
            if response.status_code == 200:
                members_data = response.json()
                if isinstance(members_data, list):
                    for member in members_data:
                        member['contact_type'] = 'member'
                    all_contacts.extend(members_data)
                    print(f"✅ Retrieved {len(members_data)} total members using /all endpoint")
                else:
                    print("⚠️ Unexpected members/all response format")
            else:
                print(f"❌ Error fetching members/all: {response.status_code}")
        except Exception as e:
            print(f"❌ Error fetching members/all: {e}")
        
        # Try prospects/all endpoint (might exist too)
        print(f"🎯 Trying prospects/all endpoint...")
        prospects_all_url = f"{self.base_url}/api/clubs/{club_id}/prospects/all"
        
        try:
            response = self.session.get(prospects_all_url, verify=False, timeout=30)
            if response.status_code == 200:
                prospects_data = response.json()
                if isinstance(prospects_data, list):
                    for prospect in prospects_data:
                        prospect['contact_type'] = 'prospect'
                    all_contacts.extend(prospects_data)
                    print(f"✅ Retrieved {len(prospects_data)} total prospects using /all endpoint")
                else:
                    print("⚠️ Unexpected prospects/all response format")
            else:
                print(f"❌ prospects/all endpoint not available: {response.status_code}")
                
                # Fallback to regular prospects endpoint with pagination
                print(f"📋 Falling back to regular prospects pagination...")
                page = 1
                all_prospects = []
                while True:
                    try:
                        params = {"page": str(page), "pageSize": "100"}
                        prospects_url = f"{self.base_url}/api/clubs/{club_id}/prospects"
                        response = self.session.get(prospects_url, params=params, verify=False, timeout=30)
                        
                        if response.status_code == 200:
                            prospects = response.json()
                            if isinstance(prospects, list) and len(prospects) > 0:
                                for prospect in prospects:
                                    prospect['contact_type'] = 'prospect'
                                all_prospects.extend(prospects)
                                print(f"  📄 Page {page}: {len(prospects)} prospects")
                                
                                if len(prospects) < 100:
                                    break
                                page += 1
                            else:
                                break
                        else:
                            break
                    except Exception as e:
                        print(f"  ❌ Error on prospects page {page}: {e}")
                        break
                
                all_contacts.extend(all_prospects)
                print(f"✅ Retrieved {len(all_prospects)} total prospects via pagination")
                
        except Exception as e:
            print(f"❌ Error trying prospects/all: {e}")
        
        return all_contacts
    
    def _get_all_paginated_data(self, base_url, data_type):
        """Get all data using pagination - aggressive approach to get ALL records"""
        all_data = []
        page = 1
        limit = 50  # API returns 50 per page
        
        print(f"  🔍 Starting pagination for {data_type}...")
        
        while True:
            # Try multiple pagination parameter combinations
            param_combinations = [
                {'page': page, 'per_page': limit},
                {'page': page, 'limit': limit},
                {'offset': (page-1) * limit, 'limit': limit},
                {'start': (page-1) * limit, 'count': limit}
            ]
            
            response = None
            data = None
            
            for params in param_combinations:
                try:
                    response = self.session.get(base_url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list) and len(data) > 0:
                            break
                except:
                    continue
            
            # If no params worked, try without params on first page
            if page == 1 and (not data or len(data) == 0):
                try:
                    response = self.session.get(base_url)
                    if response.status_code == 200:
                        data = response.json()
                except:
                    pass
            
            if data and isinstance(data, list) and len(data) > 0:
                all_data.extend(data)
                print(f"  📄 Page {page}: {len(data)} {data_type} (Total so far: {len(all_data)})")
                
                # If we got less than the limit, we're done
                if len(data) < limit:
                    print(f"  ✅ Reached end of {data_type} at page {page}")
                    break
                
                page += 1
                
                # Safety check - if we're getting a lot of pages, continue
                if page > 200:  # Allow up to 200 pages (10,000 records)
                    print(f"  ⚠️ Reached maximum page limit for {data_type}")
                    break
                    
            else:
                if page == 1:
                    print(f"  ❌ No {data_type} found or API error")
                else:
                    print(f"  ✅ Finished pagination for {data_type} at page {page}")
                break
        
        print(f"  🎯 Total {data_type} retrieved: {len(all_data)}")
        return all_data
    
    def get_prospect_details(self, prospect_id):
        """Get detailed prospect information including agreements"""
        try:
            # Get basic prospect details
            url = f"{self.base_url}/api/prospects/{prospect_id}"
            response = self.session.get(url)
            
            if response.status_code != 200:
                return None
            
            prospect_data = response.json()
            
            # Try to get agreement information
            agreement_url = f"{self.base_url}/api/prospects/{prospect_id}/agreements"
            agreement_response = self.session.get(agreement_url)
            
            if agreement_response.status_code == 200:
                prospect_data['agreements'] = agreement_response.json()
            
            return prospect_data
            
        except Exception as e:
            print(f"⚠️ Error getting details for prospect {prospect_id}: {e}")
            return None
    
    def save_to_csv(self, contacts, filename):
        """Save contacts to CSV with dynamic field mapping based on actual data"""
        print(f"💾 Saving {len(contacts)} contacts to {filename}...")
        
        if not contacts:
            print("❌ No contacts to save")
            return
        
        # Dynamically collect all field names from the actual data
        all_fields = set()
        
        print("🔍 Analyzing data structure...")
        for contact in contacts:
            # Add direct fields
            all_fields.update(contact.keys())
            
            # Handle nested objects like homeClub
            for key, value in contact.items():
                if isinstance(value, dict):
                    for nested_key in value.keys():
                        all_fields.add(f"{key}_{nested_key}")
        
        # Convert to sorted list for consistent column order
        columns = sorted(list(all_fields))
        
        print(f"📊 Found {len(columns)} unique fields in the data")
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            
            for contact in contacts:
                # Create row with flattened data
                row = {}
                
                # Handle direct fields
                for key, value in contact.items():
                    if isinstance(value, dict):
                        # Flatten nested objects
                        for nested_key, nested_value in value.items():
                            flattened_key = f"{key}_{nested_key}"
                            row[flattened_key] = str(nested_value) if nested_value is not None else ''
                    elif isinstance(value, list):
                        # Convert lists to comma-separated strings
                        row[key] = ','.join(str(item) for item in value) if value else ''
                    else:
                        row[key] = str(value) if value is not None else ''
                
                # Ensure all columns are present
                for col in columns:
                    if col not in row:
                        row[col] = ''
                
                writer.writerow(row)
        
        print(f"✅ Data saved to {filename}")
        
        # Print sample of actual data structure
        if contacts:
            sample = contacts[0]
            print(f"\n📊 SAMPLE DATA PREVIEW:")
            non_empty_fields = {k: v for k, v in sample.items() if v not in [None, '', [], {}]}
            print(f"   Total fields: {len(sample)}")
            print(f"   Non-empty fields: {len(non_empty_fields)}")
            print(f"   CSV columns: {len(columns)}")
            
            print(f"\n📋 Sample non-empty fields:")
            for key, value in list(non_empty_fields.items())[:8]:
                if isinstance(value, str) and len(value) > 40:
                    print(f"   {key}: {value[:40]}...")
                elif isinstance(value, dict):
                    print(f"   {key}: {{nested object with {len(value)} keys}}")
                else:
                    print(f"   {key}: {value}")
            if len(non_empty_fields) > 8:
                print(f"   ... and {len(non_empty_fields) - 8} more fields")
    
    def run_comprehensive_pull(self, clubs=['1156']):
        """Run comprehensive data pull for club 1156 only"""
        print("🚀 Starting comprehensive ClubHub data pull for club 1156...")
        print("=" * 60)
        
        if not self.authenticate():
            return
        
        all_contacts = []
        
        for club_id in clubs:
            print(f"\n🏢 Processing Club {club_id}...")
            contacts = self.get_prospects_and_members(club_id)
            
            # Get detailed information for each contact
            for i, contact in enumerate(contacts, 1):
                contact_id = contact.get('id')
                if contact_id and contact.get('contact_type') == 'prospect':
                    detailed = self.get_prospect_details(contact_id)
                    if detailed:
                        # Update the contact with detailed info
                        contact.update(detailed)
                    
                    if i % 10 == 0:
                        print(f"  📝 Processed {i}/{len(contacts)} contacts...")
            
            all_contacts.extend(contacts)
        
        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"master_contact_list_club1156_{timestamp}.csv"
        
        self.save_to_csv(all_contacts, filename)
        
        print(f"\n🎉 Comprehensive data pull complete!")
        print(f"📊 Total contacts: {len(all_contacts)}")
        print(f"📁 Saved to: {filename}")
        
        return filename

if __name__ == "__main__":
    puller = ClubOSDataPuller()
    puller.run_comprehensive_pull()
