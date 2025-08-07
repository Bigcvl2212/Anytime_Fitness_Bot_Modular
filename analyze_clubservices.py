#!/usr/bin/env python3
"""
Check if we can extract the training delegate ID from Dennis's account page
"""

import sys
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
from bs4 import BeautifulSoup
import json
import re

def test_clubservices_page_content():
    """Check what's on the ClubServices page"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print("🏋️ Analyzing ClubServices page content...")
    
    csv_member_id = "65828815"
    
    # Navigate to ClubServices page
    clubservices_url = f"{api.base_url}/action/Member/{csv_member_id}/clubservices"
    clubservices_response = api.session.get(clubservices_url)
    
    print(f"ClubServices page status: {clubservices_response.status_code}")
    
    if clubservices_response.status_code == 200:
        soup = BeautifulSoup(clubservices_response.text, 'html.parser')
        
        # Save the ClubServices page
        with open('dennis_clubservices_page.html', 'w', encoding='utf-8') as f:
            f.write(clubservices_response.text)
        print(f"💾 Saved ClubServices page to 'dennis_clubservices_page.html'")
        
        # Look for delegate ID on this page
        page_text = clubservices_response.text
        
        if "189425730" in page_text:
            print("✅ Found delegate ID 189425730 in ClubServices page!")
            
            # Find context around the delegate ID
            lines = page_text.split('\n')
            for i, line in enumerate(lines):
                if "189425730" in line:
                    print(f"   Line {i}: {line.strip()}")
                    # Show surrounding lines for context
                    for j in range(max(0, i-2), min(len(lines), i+3)):
                        if j != i:
                            print(f"   Line {j}: {lines[j].strip()}")
                    break
        else:
            print("❌ Delegate ID 189425730 not found in ClubServices page")
        
        # Look for any forms or actions that might trigger delegation
        forms = soup.find_all('form')
        print(f"Found {len(forms)} forms on ClubServices page")
        
        for i, form in enumerate(forms):
            action = form.get('action', 'No action')
            method = form.get('method', 'GET')
            print(f"   Form {i+1}: {method} {action}")
            
            # Look at form inputs
            inputs = form.find_all('input')
            for input_field in inputs:
                name = input_field.get('name', 'No name')
                value = input_field.get('value', '')
                input_type = input_field.get('type', 'text')
                print(f"      Input: {name} = '{value}' (type: {input_type})")
        
        # Look for any AJAX calls or JavaScript that might set delegation
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and ('delegate' in script.string.lower() or 'training' in script.string.lower()):
                print(f"   Relevant script found: {script.string[:500]}...")
        
        # Look for any links that might contain the training delegate ID
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Check if the href contains any ID that might be the delegate ID
            id_matches = re.findall(r'/(\d{8,10})/', href)
            if id_matches:
                print(f"   Link with ID: {text} -> {href} (IDs: {id_matches})")

def test_manual_delegation_with_csv_id():
    """Test manually setting delegation using CSV member ID"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print("\n🎯 Testing manual delegation with CSV member ID...")
    
    csv_member_id = "65828815"
    
    # Try the delegation endpoint directly with CSV member ID
    print(f"📝 Setting delegation to CSV member ID {csv_member_id}...")
    delegation_response = api.session.get(f"{api.base_url}/action/Delegate/{csv_member_id}/url=false")
    print(f"   Delegation status: {delegation_response.status_code}")
    
    if delegation_response.status_code == 200:
        # Now check what agreements we get
        agreements_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
        print(f"   Agreements status: {agreements_response.status_code}")
        
        if agreements_response.status_code == 200:
            agreements = agreements_response.json()
            print(f"   Found {len(agreements)} agreements with CSV ID delegation")
            
            if agreements:
                for i, agreement in enumerate(agreements):
                    package_info = agreement.get('packageAgreement', {})
                    package_name = package_info.get('name', 'No name')
                    package_member_id = package_info.get('memberId', 'No member ID')
                    print(f"      Agreement {i+1}: {package_name} (Member ID: {package_member_id})")
            else:
                print("   ❌ No agreements found with CSV ID delegation")
    
    # Now try with the known working delegate ID for comparison
    print(f"\n📝 Setting delegation to known working delegate ID 189425730...")
    delegation_response = api.session.get(f"{api.base_url}/action/Delegate/189425730/url=false")
    print(f"   Delegation status: {delegation_response.status_code}")
    
    if delegation_response.status_code == 200:
        agreements_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
        print(f"   Agreements status: {agreements_response.status_code}")
        
        if agreements_response.status_code == 200:
            agreements = agreements_response.json()
            print(f"   Found {len(agreements)} agreements with working delegate ID")
            
            if agreements:
                for i, agreement in enumerate(agreements):
                    package_info = agreement.get('packageAgreement', {})
                    package_name = package_info.get('name', 'No name')
                    package_member_id = package_info.get('memberId', 'No member ID')
                    print(f"      Agreement {i+1}: {package_name} (Member ID: {package_member_id})")

if __name__ == "__main__":
    print("🔍 Analyzing ClubServices page and testing delegation...")
    print("=" * 70)
    
    test_clubservices_page_content()
    
    test_manual_delegation_with_csv_id()
    
    print("\n" + "=" * 70)
    print("🏁 Analysis complete!")
