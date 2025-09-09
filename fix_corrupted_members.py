#!/usr/bin/env python3
"""
Emergency script to fix corrupted member names
These members had their names overwritten to NULL by the messaging client
"""

import requests
import logging
from bs4 import BeautifulSoup
import sys
import os

# Add path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.authentication.secure_secrets_manager import SecureSecretsManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClubOSMemberFixer:
    """Fix corrupted member profiles"""
    
    def __init__(self):
        secrets_manager = SecureSecretsManager()
        self.username = secrets_manager.get_secret('clubos-username')
        self.password = secrets_manager.get_secret('clubos-password')
        
        self.session = requests.Session()
        self.base_url = "https://anytime.club-os.com"
        self.authenticated = False
        
        # Set headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def authenticate(self) -> bool:
        """Authenticate with ClubOS"""
        try:
            logger.info("🔐 Authenticating...")
            
            login_url = f"{self.base_url}/action/Login/view"
            login_response = self.session.get(login_url, verify=False)
            
            soup = BeautifulSoup(login_response.text, 'html.parser')
            source_page = soup.find('input', {'name': '_sourcePage'})
            fp_token = soup.find('input', {'name': '__fp'})
            
            login_data = {
                'login': 'Submit',
                'username': self.username,
                'password': self.password,
                '_sourcePage': source_page.get('value') if source_page else '',
                '__fp': fp_token.get('value') if fp_token else ''
            }
            
            auth_response = self.session.post(
                f"{self.base_url}/action/Login",
                data=login_data,
                allow_redirects=True,
                verify=False
            )
            
            self.authenticated = True
            logger.info("✅ Authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return False
    
    def check_member_profile(self, member_id: str) -> dict:
        """Check current member profile data"""
        try:
            if not self.authenticated:
                self.authenticate()
            
            # Try to get member profile
            profile_url = f"{self.base_url}/action/LeadProfile/view/{member_id}"
            response = self.session.get(profile_url, verify=False)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for name fields
                first_name = ""
                last_name = ""
                
                # Try to find name inputs
                first_input = soup.find('input', {'name': 'firstName'}) or soup.find('input', {'id': 'firstName'})
                last_input = soup.find('input', {'name': 'lastName'}) or soup.find('input', {'id': 'lastName'})
                
                if first_input:
                    first_name = first_input.get('value', '')
                if last_input:
                    last_name = last_input.get('value', '')
                
                # Also check for display names in the page
                name_headers = soup.find_all(['h1', 'h2', 'h3'], string=True)
                for header in name_headers:
                    text = header.get_text().strip()
                    if len(text) > 0 and not text.lower().startswith(('lead', 'member', 'profile')):
                        logger.info(f"Found header text: {text}")
                
                return {
                    'member_id': member_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'profile_accessible': True,
                    'raw_response_preview': response.text[:500]
                }
            else:
                return {
                    'member_id': member_id,
                    'profile_accessible': False,
                    'error': f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                'member_id': member_id,
                'profile_accessible': False,
                'error': str(e)
            }

def main():
    """Check the corrupted members"""
    fixer = ClubOSMemberFixer()
    
    # The corrupted members from the data you showed
    corrupted_members = [
        {'id': '192224494', 'original_name': 'Kymberley Marr', 'email': 'nixon.alex53@gmail.com'},
        {'id': '189425730', 'original_name': 'Dennis Rost', 'email': 'djrost74@gmail.com'}
    ]
    
    print("🔍 Checking corrupted member profiles...")
    print("=" * 60)
    
    for member in corrupted_members:
        print(f"\n👤 Checking {member['original_name']} (ID: {member['id']})")
        
        profile_data = fixer.check_member_profile(member['id'])
        
        if profile_data['profile_accessible']:
            print(f"   ✅ Profile accessible")
            print(f"   📝 First Name: '{profile_data['first_name']}'")
            print(f"   📝 Last Name: '{profile_data['last_name']}'")
            
            if not profile_data['first_name'] and not profile_data['last_name']:
                print(f"   ❌ CONFIRMED: Names are empty/null")
                print(f"   🔧 NEEDS REPAIR: Should be '{member['original_name']}'")
            else:
                print(f"   ✅ Names appear to be present")
        else:
            print(f"   ❌ Profile not accessible: {profile_data.get('error', 'Unknown error')}")
    
    print(f"\n💡 SOLUTION: We need to manually update these member names in ClubOS")
    print(f"   - Either through the ClubOS web interface")
    print(f"   - Or by creating a proper member update API call")
    print(f"   - DO NOT use the broken messaging client anymore!")

if __name__ == "__main__":
    main()
