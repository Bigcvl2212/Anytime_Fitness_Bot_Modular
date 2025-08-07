#!/usr/bin/env python3
"""
Examine the HTML content from the action endpoints with Dennis's payment token
"""

import sys
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
from bs4 import BeautifulSoup

def examine_action_endpoint_content():
    """Examine what the action endpoints return with Dennis's payment token"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print("🔍 Examining action endpoint HTML content...")
    print("=" * 70)
    
    dennis_token = "8d4b4880-39dd-4a6a-b3d4-0b3a7c9fc02f"
    
    # Test the action endpoints that returned 65,002 character responses
    action_endpoints = [
        f"/action/Agreement/token/{dennis_token}",
        f"/action/Payment/token/{dennis_token}",
        f"/action/Agreement/1598572",  # Dennis's agreement ID
    ]
    
    for endpoint in action_endpoints:
        print(f"\n📄 Examining: {endpoint}")
        
        try:
            response = api.session.get(f"{api.base_url}{endpoint}")
            
            if response.status_code == 200:
                print(f"   Response length: {len(response.text)} characters")
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for key information
                title = soup.find('title')
                if title:
                    print(f"   Page title: {title.get_text().strip()}")
                
                # Look for training/package related content
                page_text = response.text.lower()
                training_keywords = ['training', 'package', 'agreement', 'dennis', 'rost', '1598572', '189425730']
                
                print(f"   Content analysis:")
                for keyword in training_keywords:
                    count = page_text.count(keyword)
                    if count > 0:
                        print(f"     '{keyword}': {count} mentions")
                
                # Look for forms and their inputs
                forms = soup.find_all('form')
                print(f"   Found {len(forms)} forms")
                
                for i, form in enumerate(forms[:3]):  # Show first 3 forms
                    action = form.get('action', 'No action')
                    method = form.get('method', 'GET')
                    print(f"     Form {i+1}: {method} {action}")
                    
                    # Look for interesting inputs
                    inputs = form.find_all('input')
                    for input_field in inputs:
                        name = input_field.get('name', '')
                        value = input_field.get('value', '')
                        input_type = input_field.get('type', 'text')
                        
                        if any(keyword in name.lower() for keyword in ['id', 'member', 'agreement', 'token']):
                            print(f"       Input: {name} = '{value}' (type: {input_type})")
                
                # Look for any JavaScript that might contain useful data
                scripts = soup.find_all('script')
                print(f"   Found {len(scripts)} script tags")
                
                for script in scripts:
                    if script.string:
                        script_text = script.string.lower()
                        # Look for IDs or data structures
                        if any(keyword in script_text for keyword in ['189425730', '1598572', 'dennis', 'packageagreement']):
                            print(f"     Script contains relevant data: {script.string[:200]}...")
                
                # Look for any data tables
                tables = soup.find_all('table')
                if tables:
                    print(f"   Found {len(tables)} tables")
                    for i, table in enumerate(tables[:2]):  # Show first 2 tables
                        rows = table.find_all('tr')
                        if rows:
                            print(f"     Table {i+1}: {len(rows)} rows")
                            # Show first few cells if they contain useful data
                            for j, row in enumerate(rows[:3]):
                                cells = row.find_all(['td', 'th'])
                                if cells:
                                    cell_text = [cell.get_text().strip()[:50] for cell in cells[:5]]
                                    print(f"       Row {j+1}: {cell_text}")
                
                # Save the HTML for manual inspection
                filename = f"action_endpoint_{endpoint.replace('/', '_').replace(':', '')}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"   💾 Saved HTML to: {filename}")
                
            else:
                print(f"   ❌ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_delegation_after_token_access():
    """Test if accessing token endpoints affects delegation state"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print(f"\n🔄 Testing delegation after token access...")
    print("=" * 70)
    
    dennis_token = "8d4b4880-39dd-4a6a-b3d4-0b3a7c9fc02f"
    
    # First, access the token endpoint
    print("📝 Step 1: Accessing token endpoint...")
    token_response = api.session.get(f"{api.base_url}/action/Agreement/token/{dennis_token}")
    print(f"   Token endpoint status: {token_response.status_code}")
    
    # Then try to get package agreements
    print("📝 Step 2: Testing package agreements after token access...")
    agreements_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
    print(f"   Agreements status: {agreements_response.status_code}")
    
    if agreements_response.status_code == 200:
        agreements = agreements_response.json()
        print(f"   Found {len(agreements)} agreements!")
        
        if agreements:
            for i, agreement in enumerate(agreements):
                package_info = agreement.get('packageAgreement', {})
                name = package_info.get('name', 'No name')
                member_id = package_info.get('memberId', 'No member ID')
                agreement_id = package_info.get('id', 'No agreement ID')
                print(f"     Agreement {i+1}: {name} (Member: {member_id}, Agreement: {agreement_id})")
        else:
            print("   No agreements found")
    
    # Test agreement ID endpoint
    print("📝 Step 3: Testing agreement ID endpoint...")
    agreement_response = api.session.get(f"{api.base_url}/action/Agreement/1598572")
    print(f"   Agreement ID endpoint status: {agreement_response.status_code}")
    
    # Then try package agreements again
    print("📝 Step 4: Testing package agreements after agreement access...")
    agreements_response2 = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
    print(f"   Agreements status: {agreements_response2.status_code}")
    
    if agreements_response2.status_code == 200:
        agreements2 = agreements_response2.json()
        print(f"   Found {len(agreements2)} agreements!")

if __name__ == "__main__":
    examine_action_endpoint_content()
    test_delegation_after_token_access()
    
    print("\n" + "=" * 70)
    print("🏁 Action endpoint analysis complete!")
