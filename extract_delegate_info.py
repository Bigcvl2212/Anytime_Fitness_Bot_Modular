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

def extract_delegate_id_from_account():
    """Try to extract the training delegate ID from Dennis's account page"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print("🔍 Extracting delegate ID from Dennis's account page...")
    
    # Use Dennis's CSV member ID
    csv_member_id = "65828815"
    
    # Get his account page
    print(f"📝 Getting account page for member ID {csv_member_id}...")
    account_url = f"{api.base_url}/action/Member/{csv_member_id}/view"
    account_response = api.session.get(account_url)
    
    print(f"Account page status: {account_response.status_code}")
    
    if account_response.status_code == 200:
        soup = BeautifulSoup(account_response.text, 'html.parser')
        
        # Save the account page HTML for inspection
        with open('dennis_account_page.html', 'w', encoding='utf-8') as f:
            f.write(account_response.text)
        print(f"💾 Saved account page to 'dennis_account_page.html'")
        
        # Look for any references to the delegate ID (189425730)
        page_text = account_response.text
        
        print(f"\n🔍 Searching for delegate ID 189425730 in page...")
        if "189425730" in page_text:
            print("✅ Found delegate ID 189425730 in account page!")
            
            # Find the context around it
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
            print("❌ Delegate ID 189425730 not found in account page")
        
        # Look for any ClubServices or training-related links
        print(f"\n🔍 Looking for ClubServices/training links...")
        
        # Find all links
        links = soup.find_all('a', href=True)
        training_links = []
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if any(keyword in href.lower() for keyword in ['clubservices', 'training', 'package', 'agreement']):
                training_links.append((href, text))
            elif any(keyword in text.lower() for keyword in ['training', 'package', 'clubservices']):
                training_links.append((href, text))
        
        print(f"Found {len(training_links)} potential training-related links:")
        for href, text in training_links:
            print(f"   {text}: {href}")
        
        # Look for any JavaScript variables or data attributes that might contain the delegate ID
        print(f"\n🔍 Looking for JavaScript data...")
        
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for any number that matches our delegate ID pattern
                numbers = re.findall(r'\b\d{8,10}\b', script.string)
                if numbers:
                    print(f"   Found numbers in script: {numbers}")
                    if "189425730" in numbers:
                        print(f"   ✅ Found delegate ID in JavaScript!")
        
        # Look for data attributes
        elements_with_data = soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys()))
        for element in elements_with_data:
            for attr, value in element.attrs.items():
                if attr.startswith('data-') and str(value).isdigit() and len(str(value)) >= 8:
                    print(f"   Data attribute {attr}: {value}")

def test_clubservices_page_content():
    """Check what's on the ClubServices page"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print("\n🏋️ Analyzing ClubServices page content...")
    
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
        else:
            print("❌ Delegate ID 189425730 not found in ClubServices page")
        
        # Look for any forms or actions that might trigger delegation
        forms = soup.find_all('form')
        print(f"Found {len(forms)} forms on ClubServices page")
        
        for i, form in enumerate(forms):
            action = form.get('action', 'No action')
            method = form.get('method', 'GET')
            print(f"   Form {i+1}: {method} {action}")
        
        # Look for any AJAX calls or JavaScript that might set delegation
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and ('delegate' in script.string.lower() or 'training' in script.string.lower()):
                print(f"   Relevant script found: {script.string[:200]}...")

if __name__ == "__main__":
    print("🔍 Extracting training delegate information from Dennis's account...")
    print("=" * 70)
    
    extract_delegate_id_from_account()
    
    test_clubservices_page_content()
    
    print("\n" + "=" * 70)
    print("🏁 Analysis complete!")
