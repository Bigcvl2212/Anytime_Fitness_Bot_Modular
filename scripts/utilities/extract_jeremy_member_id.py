#!/usr/bin/env python3
"""
Extract Jeremy Mayo's Member ID from ClubOS HTML
"""

from src.services.api.clubos_api_client import ClubOSAPIClient
from bs4 import BeautifulSoup
import re

def extract_jeremy_member_id():
    """Extract Jeremy Mayo's member ID from the ClubOS search results"""
    
    print("🔍 Extracting Jeremy Mayo's member ID from ClubOS...")
    
    client = ClubOSAPIClient()
    if not client.authenticate():
        print("❌ Authentication failed")
        return None
    
    # Get the raw HTML response
    headers = client.auth.get_headers()
    response = client.auth.session.get(
        f"{client.base_url}/action/UserSearch",
        params={"q": "Jeremy Mayo"},
        headers=headers,
        timeout=30,
        verify=False
    )
    
    if not response.ok:
        print(f"❌ Search failed: {response.status_code}")
        return None
    
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print("🔍 Analyzing HTML structure...")
    
    # Look for Jeremy Mayo specifically
    jeremy_patterns = [
        r'Jeremy\s+Mayo',
        r'jeremy\s+mayo',
        r'JEREMY\s+MAYO'
    ]
    
    # Search in all text content
    text_content = soup.get_text()
    for pattern in jeremy_patterns:
        matches = re.findall(pattern, text_content, re.IGNORECASE)
        if matches:
            print(f"✅ Found 'Jeremy Mayo' in text content")
            break
    
    # Look for the specific div that contains Jeremy's data
    jeremy_div = soup.find('div', class_='search-result', string=re.compile(r'Jeremy Mayo', re.IGNORECASE))
    if not jeremy_div:
        # Try to find by text content
        for div in soup.find_all('div', class_='search-result'):
            if 'jeremy mayo' in div.get_text().lower():
                jeremy_div = div
                break
    
    if jeremy_div:
        print(f"✅ Found Jeremy Mayo's div:")
        print(f"   Text: {jeremy_div.get_text(strip=True)}")
        print(f"   Data ID: {jeremy_div.get('data-id')}")
        print(f"   All attributes: {jeremy_div.attrs}")
        print()
        
        # Look for 8-digit numbers in the div or its children
        div_text = jeremy_div.get_text()
        eight_digit_numbers = re.findall(r'\b\d{8}\b', div_text)
        print(f"🔍 8-digit numbers found in div: {eight_digit_numbers}")
        
        # Look for prospectID in any attributes or data fields
        for attr_name, attr_value in jeremy_div.attrs.items():
            if 'prospect' in attr_name.lower() or 'id' in attr_name.lower():
                print(f"   {attr_name}: {attr_value}")
        
        # Check parent elements for prospectID
        parent = jeremy_div.parent
        if parent:
            print(f"🔍 Checking parent element:")
            print(f"   Parent tag: {parent.name}")
            print(f"   Parent attributes: {parent.attrs}")
            for attr_name, attr_value in parent.attrs.items():
                if 'prospect' in attr_name.lower() or 'id' in attr_name.lower():
                    print(f"   Parent {attr_name}: {attr_value}")
        
        # Look for any onclick handlers that might contain prospectID
        onclick_attr = jeremy_div.get('onclick')
        if onclick_attr:
            print(f"🔍 Onclick handler: {onclick_attr}")
            # Look for 8-digit numbers in onclick
            onclick_numbers = re.findall(r'\b\d{8}\b', onclick_attr)
            print(f"   8-digit numbers in onclick: {onclick_numbers}")
    
    # Look for any elements with prospectID in their attributes
    prospect_elements = soup.find_all(attrs=lambda x: any('prospect' in str(k).lower() for k in x.keys() if x))
    print(f"🔍 Found {len(prospect_elements)} elements with prospect-related attributes")
    
    for elem in prospect_elements:
        elem_text = elem.get_text(strip=True)
        if 'jeremy' in elem_text.lower() or 'mayo' in elem_text.lower():
            print(f"✅ Found Jeremy Mayo element with prospect attributes:")
            print(f"   Text: {elem_text}")
            print(f"   Attributes: {elem.attrs}")
            print()
    
    # Look for any 8-digit numbers in the entire HTML
    all_eight_digit_numbers = re.findall(r'\b\d{8}\b', html_content)
    print(f"🔍 All 8-digit numbers found in HTML: {all_eight_digit_numbers}")
    
    # Look for any elements with data-prospect-id or similar attributes
    prospect_id_elements = soup.find_all(attrs={'data-prospect-id': True})
    prospect_id_elements.extend(soup.find_all(attrs=lambda x: any('prospect' in str(k).lower() and 'id' in str(k).lower() for k in x.keys() if x)))
    
    print(f"🔍 Found {len(prospect_id_elements)} elements with prospect ID attributes")
    for elem in prospect_id_elements:
        elem_text = elem.get_text(strip=True)
        if 'jeremy' in elem_text.lower() or 'mayo' in elem_text.lower():
            print(f"✅ Found Jeremy Mayo element with prospect ID:")
            print(f"   Text: {elem_text}")
            print(f"   All attributes: {elem.attrs}")
            print()
    
    return None

if __name__ == "__main__":
    member_id = extract_jeremy_member_id()
    if member_id:
        print(f"🎯 Jeremy Mayo's Member ID: {member_id}")
    else:
        print("❌ Could not extract member ID") 