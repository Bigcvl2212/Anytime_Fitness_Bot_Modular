#!/usr/bin/env python3
"""
Emergency repair script to restore corrupted member names
Uses the actual names from HAR analysis to fix the damage
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

class ClubOSMemberRepairer:
    """Repair corrupted member profiles with correct names"""
    
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
    
    def repair_member_name(self, member_id: str, first_name: str, last_name: str, email: str, phone: str) -> bool:
        """Repair a member's corrupted name"""
        try:
            if not self.authenticated:
                self.authenticate()
            
            logger.info(f"🔧 Repairing member {member_id}: {first_name} {last_name}")
            
            # Step 1: Get the member's edit form
            edit_url = f"{self.base_url}/action/LeadProfile/edit/{member_id}"
            edit_response = self.session.get(edit_url, verify=False)
            
            if edit_response.status_code != 200:
                logger.error(f"❌ Could not access edit form for {member_id}")
                return False
            
            # Step 2: Extract form tokens and existing data
            soup = BeautifulSoup(edit_response.text, 'html.parser')
            
            csrf_token = ""
            fp_token = ""
            source_page = ""
            
            csrf_input = soup.find('input', {'name': '__RequestVerificationToken'})
            if csrf_input:
                csrf_token = csrf_input.get('value', '')
            
            fp_input = soup.find('input', {'name': '__fp'})
            if fp_input:
                fp_token = fp_input.get('value', '')
            
            source_input = soup.find('input', {'name': '_sourcePage'})
            if source_input:
                source_page = source_input.get('value', '')
            
            # Step 3: Find all existing form fields to preserve other data
            form_data = {
                # Core identification
                "tfoUserId": member_id,
                
                # Names (THE FIX!)
                "firstName": first_name,
                "lastName": last_name,
                
                # Contact info
                "email": email,
                "mobilePhone": phone,
                
                # Security tokens
                "__RequestVerificationToken": csrf_token,
                "__fp": fp_token,
                "_sourcePage": source_page,
                
                # Common required fields
                "save": "Save",
                "leadType": "Member",  # Assuming they're members
            }
            
            # Try to preserve existing form fields
            for input_field in soup.find_all('input'):
                name = input_field.get('name', '')
                value = input_field.get('value', '')
                
                # Skip the fields we're specifically fixing
                if name in ['firstName', 'lastName', '__RequestVerificationToken', '__fp', '_sourcePage']:
                    continue
                
                # Skip empty names
                if not name:
                    continue
                
                # Add other fields to preserve existing data
                if name not in form_data:
                    form_data[name] = value
            
            # Step 4: Submit the repair
            save_url = f"{self.base_url}/action/LeadProfile/save"
            
            save_headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": edit_url
            }
            
            save_response = self.session.post(save_url, data=form_data, headers=save_headers, verify=False)
            
            if save_response.status_code == 200:
                # Check if redirect indicates success
                if 'LeadProfile/view' in save_response.url or save_response.history:
                    logger.info(f"✅ Successfully repaired {first_name} {last_name} (ID: {member_id})")
                    return True
                else:
                    logger.warning(f"⚠️ Uncertain repair status for {member_id}")
                    logger.warning(f"Response preview: {save_response.text[:200]}")
                    return False
            else:
                logger.error(f"❌ Failed to save repair for {member_id}: HTTP {save_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error repairing member {member_id}: {e}")
            return False

def main():
    """Repair the corrupted members with their actual names from HAR"""
    repairer = ClubOSMemberRepairer()
    
    # The corrupted members with their ACTUAL names from HAR analysis
    corrupted_members = [
        {
            'id': '192224494',
            'first_name': 'Kymberley',
            'last_name': 'Marr', 
            'email': 'nixon.alex53@gmail.com',
            'phone': '+1 (765) 271-6832'
        },
        {
            'id': '189425730',
            'first_name': 'Dennis',
            'last_name': 'Rost',
            'email': 'djrost74@gmail.com', 
            'phone': '(920) 933-0520'
        }
    ]
    
    print("🚑 EMERGENCY REPAIR: Fixing corrupted member profiles...")
    print("=" * 60)
    
    repair_count = 0
    
    for member in corrupted_members:
        print(f"\n🔧 Repairing: {member['first_name']} {member['last_name']} (ID: {member['id']})")
        
        success = repairer.repair_member_name(
            member_id=member['id'],
            first_name=member['first_name'],
            last_name=member['last_name'],
            email=member['email'],
            phone=member['phone']
        )
        
        if success:
            repair_count += 1
            print(f"   ✅ REPAIRED: {member['first_name']} {member['last_name']}")
        else:
            print(f"   ❌ FAILED: Could not repair {member['id']}")
    
    print(f"\n📊 REPAIR SUMMARY:")
    print(f"   🔧 Attempted: {len(corrupted_members)} profiles")
    print(f"   ✅ Successful: {repair_count} profiles") 
    print(f"   ❌ Failed: {len(corrupted_members) - repair_count} profiles")
    
    if repair_count == len(corrupted_members):
        print(f"\n🎉 ALL PROFILES SUCCESSFULLY REPAIRED!")
        print(f"   Members should now be clickable in ClubOS again.")
    else:
        print(f"\n⚠️ Some repairs failed. You may need to fix manually in ClubOS web interface.")

if __name__ == "__main__":
    main()
