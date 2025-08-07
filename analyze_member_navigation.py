#!/usr/bin/env python3
"""
Analyze the member search page to understand how to search for Dennis
"""

import sys
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
from bs4 import BeautifulSoup
import json
import re

def analyze_member_search_page():
    """Analyze the member search page to understand the workflow"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print("🔍 Analyzing ClubOS member search page...")
    
    # Get the member search page
    search_url = f"{api.base_url}/action/Members/search"
    response = api.session.get(search_url)
    
    print(f"Search page status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for forms
        forms = soup.find_all('form')
        print(f"Found {len(forms)} forms on the page")
        
        for i, form in enumerate(forms):
            print(f"\nForm {i+1}:")
            print(f"  Action: {form.get('action', 'No action')}")
            print(f"  Method: {form.get('method', 'GET')}")
            
            # Look for input fields
            inputs = form.find_all('input')
            for input_field in inputs:
                name = input_field.get('name', 'No name')
                input_type = input_field.get('type', 'text')
                value = input_field.get('value', '')
                print(f"    Input: {name} (type: {input_type}, value: '{value}')")
        
        # Look for any JavaScript that might handle search
        scripts = soup.find_all('script')
        print(f"\nFound {len(scripts)} script tags")
        
        for i, script in enumerate(scripts):
            if script.string and ('search' in script.string.lower() or 'member' in script.string.lower()):
                print(f"\nRelevant script {i+1}:")
                print(script.string[:500] + "..." if len(script.string) > 500 else script.string)
        
        # Look for any AJAX endpoints or data attributes
        ajax_elements = soup.find_all(attrs={"data-url": True})
        for element in ajax_elements:
            print(f"AJAX endpoint found: {element.get('data-url')}")
        
        # Save the HTML for manual inspection
        with open('member_search_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\n💾 Saved search page HTML to 'member_search_page.html'")

def test_direct_member_navigation():
    """Test directly navigating to Dennis using his known CSV member ID"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print("\n🎯 Testing direct navigation to Dennis using CSV member ID...")
    
    # Use Dennis's CSV member ID
    csv_member_id = "65828815"
    
    # Step 1: Try to navigate directly to his account page
    print(f"📝 Step 1: Direct navigation to account page for ID {csv_member_id}...")
    account_url = f"{api.base_url}/action/Member/{csv_member_id}/view"
    account_response = api.session.get(account_url)
    print(f"   Account page status: {account_response.status_code}")
    
    if account_response.status_code == 200:
        # Step 2: Navigate to ClubServices page
        print(f"🏋️ Step 2: Navigating to ClubServices page...")
        clubservices_url = f"{api.base_url}/action/Member/{csv_member_id}/clubservices"
        clubservices_response = api.session.get(clubservices_url)
        print(f"   ClubServices page status: {clubservices_response.status_code}")
        
        if clubservices_response.status_code == 200:
            # Step 3: Check if delegate context is now set
            print(f"📦 Step 3: Testing package agreements after navigation...")
            agreements_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
            print(f"   Agreements status: {agreements_response.status_code}")
            
            if agreements_response.status_code == 200:
                agreements = agreements_response.json()
                print(f"   ✅ Found {len(agreements)} agreements after navigation!")
                
                if agreements:
                    for i, agreement in enumerate(agreements):
                        package_info = agreement.get('packageAgreement', {})
                        package_name = package_info.get('name', 'No name')
                        package_member_id = package_info.get('memberId', 'No member ID')
                        print(f"      Agreement {i+1}: {package_name} (Member ID: {package_member_id})")
                        
                        # Check if this member ID matches our known working delegate ID
                        if str(package_member_id) == "189425730":
                            print(f"      🎯 BINGO! This matches Dennis's working delegate ID!")
                else:
                    print("   ❌ No agreements found")
            else:
                print(f"   ❌ Failed to get agreements: {agreements_response.status_code}")
        else:
            print(f"   ❌ Failed to load ClubServices page: {clubservices_response.status_code}")
            
            # Try alternative ClubServices URLs
            alt_urls = [
                f"{api.base_url}/action/Member/{csv_member_id}/clubservices/view",
                f"{api.base_url}/action/ClubServices/{csv_member_id}",
                f"{api.base_url}/action/Member/{csv_member_id}/services"
            ]
            
            for alt_url in alt_urls:
                print(f"   Trying alternative URL: {alt_url}")
                alt_response = api.session.get(alt_url)
                print(f"      Status: {alt_response.status_code}")
                
                if alt_response.status_code == 200:
                    print(f"      ✅ Alternative URL worked! Testing agreements...")
                    agreements_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
                    if agreements_response.status_code == 200:
                        agreements = agreements_response.json()
                        print(f"      Found {len(agreements)} agreements!")
                    break
    else:
        print(f"   ❌ Failed to load account page: {account_response.status_code}")
        print(f"   Response: {account_response.text[:200]}...")

if __name__ == "__main__":
    print("🔍 Analyzing ClubOS member navigation workflow...")
    print("=" * 70)
    
    analyze_member_search_page()
    
    print("\n" + "=" * 70)
    
    test_direct_member_navigation()
    
    print("\n" + "=" * 70)
    print("🏁 Analysis complete!")
