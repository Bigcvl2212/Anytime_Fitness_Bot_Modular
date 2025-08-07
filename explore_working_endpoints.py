#!/usr/bin/env python3
"""
Explore the working /action/ endpoints to extract training data
"""

import sys
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
from bs4 import BeautifulSoup
import json
import re

def explore_action_endpoints():
    """Explore the working /action/ endpoints to find training data"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print("🔍 Exploring working /action/ endpoints...")
    print("=" * 70)
    
    # The endpoints that returned 200 status
    working_endpoints = [
        "/action/Training",
        "/action/Packages", 
        "/action/Agreements",
        "/action/ClubServices",
    ]
    
    for endpoint in working_endpoints:
        print(f"\n📍 Analyzing: {endpoint}")
        
        try:
            response = api.session.get(f"{api.base_url}{endpoint}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Save the HTML for inspection
                filename = f"page_{endpoint.replace('/', '_').replace('action_', '')}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"   💾 Saved HTML to: {filename}")
                
                # Look for training client data
                print(f"   🔍 Searching for training client data...")
                
                # Look for JavaScript data
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        # Look for JSON data in JavaScript
                        json_matches = re.findall(r'({[^{}]*"[^"]*"[^{}]*})', script.string)
                        for match in json_matches:
                            try:
                                data = json.loads(match)
                                if any(key in str(data).lower() for key in ['training', 'package', 'agreement', 'member']):
                                    print(f"   📊 Found relevant JS data: {json.dumps(data, indent=2)[:200]}...")
                            except:
                                pass
                        
                        # Look for member IDs or training IDs
                        id_matches = re.findall(r'\b\d{8,10}\b', script.string)
                        if id_matches:
                            unique_ids = list(set(id_matches))[:10]  # Show first 10 unique IDs
                            print(f"   🆔 Found IDs in JS: {unique_ids}")
                
                # Look for forms that might submit training data
                forms = soup.find_all('form')
                print(f"   📝 Found {len(forms)} forms")
                
                for i, form in enumerate(forms):
                    action = form.get('action', 'No action')
                    method = form.get('method', 'GET')
                    if 'training' in action.lower() or 'package' in action.lower():
                        print(f"     Form {i+1}: {method} {action}")
                        
                        # Look at form inputs
                        inputs = form.find_all('input')
                        for input_field in inputs:
                            name = input_field.get('name', '')
                            value = input_field.get('value', '')
                            if name and ('id' in name.lower() or 'member' in name.lower()):
                                print(f"       Input: {name} = '{value}'")
                
                # Look for tables that might contain member/training data
                tables = soup.find_all('table')
                print(f"   📋 Found {len(tables)} tables")
                
                for i, table in enumerate(tables):
                    # Look for table headers
                    headers = table.find_all(['th', 'td'])
                    header_text = ' '.join([h.get_text(strip=True) for h in headers[:10]])  # First 10 cells
                    
                    if any(keyword in header_text.lower() for keyword in ['training', 'package', 'member', 'client', 'agreement']):
                        print(f"     Table {i+1} (relevant): {header_text[:100]}...")
                        
                        # Get some row data
                        rows = table.find_all('tr')[:5]  # First 5 rows
                        for j, row in enumerate(rows):
                            cells = row.find_all(['td', 'th'])
                            row_text = ' | '.join([cell.get_text(strip=True) for cell in cells])
                            if row_text.strip():
                                print(f"       Row {j+1}: {row_text[:100]}...")
                
                # Look for any links that might lead to training data
                links = soup.find_all('a', href=True)
                training_links = []
                
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    if any(keyword in href.lower() or keyword in text.lower() 
                           for keyword in ['training', 'package', 'agreement', 'client']):
                        training_links.append((text, href))
                
                if training_links:
                    print(f"   🔗 Found {len(training_links)} training-related links:")
                    for text, href in training_links[:10]:  # Show first 10
                        print(f"     {text}: {href}")
                
        except Exception as e:
            print(f"   ❌ Error analyzing {endpoint}: {e}")

def test_training_page_with_delegation():
    """Test the training page after setting delegation to see if data appears"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print(f"\n🎯 Testing training page with delegation set...")
    print("=" * 70)
    
    # Set delegation to Dennis's ID
    print("📝 Setting delegation to Dennis's ID (189425730)...")
    delegation_response = api.session.get(f"{api.base_url}/action/Delegate/189425730/url=false")
    print(f"   Delegation status: {delegation_response.status_code}")
    
    if delegation_response.status_code == 200:
        # Now check the training pages
        training_pages = [
            "/action/Training",
            "/action/Packages",
            "/action/Agreements",
        ]
        
        for page in training_pages:
            print(f"\n📄 Checking {page} with delegation set...")
            
            try:
                response = api.session.get(f"{api.base_url}{page}")
                
                if response.status_code == 200:
                    # Check if Dennis's data appears
                    content = response.text.lower()
                    
                    # Look for Dennis-specific data
                    dennis_indicators = [
                        "dennis",
                        "rost", 
                        "189425730",  # His delegate ID
                        "65828815",   # His CSV ID
                        "2025 1x1 training",  # His package
                        "djrost74",   # His email
                    ]
                    
                    found_indicators = []
                    for indicator in dennis_indicators:
                        if indicator in content:
                            found_indicators.append(indicator)
                    
                    if found_indicators:
                        print(f"   ✅ Found Dennis data: {found_indicators}")
                        
                        # Save this page for detailed analysis
                        filename = f"page_with_delegation_{page.replace('/', '_').replace('action_', '')}.html"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"   💾 Saved delegated page to: {filename}")
                    else:
                        print(f"   ❌ No Dennis-specific data found")
                        
            except Exception as e:
                print(f"   ❌ Error checking {page}: {e}")

def search_for_training_client_lists():
    """Search for endpoints that might list all training clients"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print(f"\n🔍 Searching for training client list endpoints...")
    print("=" * 70)
    
    # Try various list endpoints
    list_endpoints = [
        "/action/Training/list",
        "/action/Training/clients/list", 
        "/action/Packages/list",
        "/action/Agreements/list",
        "/action/Members/training",
        "/action/Members/packages",
        "/action/ClubServices/members",
        "/action/ClubServices/training/list",
        "/action/Reports/training",
        "/action/Reports/packages",
        "/action/Dashboard/training",
    ]
    
    for endpoint in list_endpoints:
        print(f"\n📍 Testing: {endpoint}")
        
        try:
            response = api.session.get(f"{api.base_url}{endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS! Length: {len(response.text)}")
                
                # Check if it contains multiple member data
                content = response.text.lower()
                
                # Count potential member references
                member_indicators = len(re.findall(r'\b\d{8,10}\b', response.text))
                email_indicators = len(re.findall(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', response.text))
                
                print(f"   📊 Found ~{member_indicators} potential member IDs")
                print(f"   📧 Found ~{email_indicators} email addresses")
                
                if member_indicators > 5 or email_indicators > 5:
                    print(f"   🎯 Looks like a member list! Saving for analysis...")
                    filename = f"potential_member_list_{endpoint.replace('/', '_').replace('action_', '')}.html"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"   💾 Saved to: {filename}")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    explore_action_endpoints()
    test_training_page_with_delegation()
    search_for_training_client_lists()
    
    print("\n" + "=" * 70)
    print("🏁 Exploration complete!")
