#!/usr/bin/env python3
"""
Extract Jeremy Mayo's precise member ID from ClubOS search results
"""

from src.services.api.clubos_api_client import ClubOSAPIClient
from config.secrets_local import get_secret
from bs4 import BeautifulSoup
import re
import json

def extract_jeremy_member_id():
    """Extract Jeremy Mayo's precise member ID from search results"""
    
    print("🔍 Extracting Jeremy Mayo's precise member ID...")
    print("=" * 60)
    
    # Create API client and authenticate
    client = ClubOSAPIClient()
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    print("1. Authenticating with ClubOS...")
    if not client.auth.login(username, password):
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Get the search results
    headers = client.auth.get_headers()
    
    try:
        response = client.auth.session.get(
            f"{client.base_url}/action/UserSearch",
            params={"q": "Jeremy Mayo"},
            headers=headers,
            timeout=30,
            verify=False
        )
        
        if response.status_code != 200:
            print(f"❌ Search failed: {response.status_code}")
            return
        
        print("2. Parsing search results...")
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for Jeremy Mayo specifically in the HTML structure
        print("3. Looking for Jeremy Mayo in HTML structure...")
        
        # Method 1: Look for links that contain Jeremy Mayo
        jeremy_links = []
        for link in soup.find_all('a'):
            link_text = link.get_text().strip()
            if 'jeremy' in link_text.lower() and 'mayo' in link_text.lower():
                jeremy_links.append({
                    'text': link_text,
                    'href': link.get('href', ''),
                    'id': link.get('id', ''),
                    'class': link.get('class', [])
                })
        
        print(f"   Found {len(jeremy_links)} links containing 'Jeremy Mayo':")
        for link in jeremy_links:
            print(f"   - Text: {link['text']}")
            print(f"   - Href: {link['href']}")
            print(f"   - ID: {link['id']}")
            print(f"   - Class: {link['class']}")
        
        # Method 2: Look for table rows containing Jeremy Mayo
        jeremy_rows = []
        for row in soup.find_all(['tr', 'div']):
            row_text = row.get_text().lower()
            if 'jeremy' in row_text and 'mayo' in row_text:
                jeremy_rows.append({
                    'tag': row.name,
                    'text': row.get_text()[:200],
                    'id': row.get('id', ''),
                    'class': row.get('class', [])
                })
        
        print(f"\n   Found {len(jeremy_rows)} rows/divs containing 'Jeremy Mayo':")
        for row in jeremy_rows:
            print(f"   - Tag: {row['tag']}")
            print(f"   - Text: {row['text']}")
            print(f"   - ID: {row['id']}")
            print(f"   - Class: {row['class']}")
        
        # Method 3: Extract all member IDs and their context
        print(f"\n4. Extracting all member IDs with context...")
        
        # Look for data attributes that might contain member IDs
        data_attrs = soup.find_all(attrs={"data-member-id": True})
        print(f"   Found {len(data_attrs)} elements with data-member-id:")
        for elem in data_attrs:
            member_id = elem.get('data-member-id')
            elem_text = elem.get_text()[:100]
            print(f"   - ID: {member_id}, Text: {elem_text}")
        
        # Look for onclick attributes that might contain member IDs
        onclick_elems = soup.find_all(attrs={"onclick": True})
        jeremy_onclick = []
        for elem in onclick_elems:
            onclick = elem.get('onclick', '')
            if 'jeremy' in elem.get_text().lower() or 'mayo' in elem.get_text().lower():
                jeremy_onclick.append({
                    'text': elem.get_text()[:100],
                    'onclick': onclick
                })
        
        print(f"   Found {len(jeremy_onclick)} elements with onclick containing Jeremy:")
        for elem in jeremy_onclick:
            print(f"   - Text: {elem['text']}")
            print(f"   - Onclick: {elem['onclick']}")
        
        # Method 4: Look for JavaScript that might contain member data
        scripts = soup.find_all('script')
        jeremy_script_data = []
        for script in scripts:
            script_text = script.get_text()
            if 'jeremy' in script_text.lower() and 'mayo' in script_text.lower():
                jeremy_script_data.append(script_text[:500])
        
        print(f"\n   Found {len(jeremy_script_data)} scripts containing Jeremy Mayo:")
        for i, script in enumerate(jeremy_script_data):
            print(f"   - Script {i+1}: {script}")
        
        # Method 5: Look for specific patterns in the HTML
        print(f"\n5. Looking for specific member ID patterns...")
        
        # Look for URLs that might contain member IDs
        url_pattern = r'/action/[^"]*/(\d+)'
        url_matches = re.findall(url_pattern, response.text)
        print(f"   Found {len(url_matches)} potential member IDs in URLs: {url_matches}")
        
        # Look for member ID patterns in the text
        id_patterns = [
            r'Member ID[:\s]*(\d+)',
            r'ID[:\s]*(\d+)',
            r'Member[:\s]*(\d+)',
            r'data-member-id="(\d+)"',
            r'data-user-id="(\d+)"',
            r'data-id="(\d+)"'
        ]
        
        for pattern in id_patterns:
            matches = re.findall(pattern, response.text, re.IGNORECASE)
            if matches:
                print(f"   Pattern '{pattern}': {matches}")
        
        # Save the full response for manual inspection
        with open('jeremy_search_results.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"\n6. Saved full search results to 'jeremy_search_results.html'")
        print(f"   You can manually inspect this file to find the exact member ID")
        
        return {
            'jeremy_links': jeremy_links,
            'jeremy_rows': jeremy_rows,
            'data_attrs': [elem.get('data-member-id') for elem in data_attrs],
            'url_matches': url_matches,
            'html_file': 'jeremy_search_results.html'
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    extract_jeremy_member_id() 