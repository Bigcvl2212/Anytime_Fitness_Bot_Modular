#!/usr/bin/env python3
"""Debug assignees HTML parsing."""

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI
from bs4 import BeautifulSoup
import re

def debug_assignees_html():
    """Debug the assignees HTML parsing."""
    
    api = ClubOSTrainingPackageAPI()
    print('🔐 Authenticating...')
    
    if api.authenticate():
        print('✅ Authentication successful')
        
        # Manually fetch the assignees page
        url = f"{api.base_url}/action/Assignees"
        headers = {
            'User-Agent': api.session.headers.get('User-Agent', 'Mozilla/5.0'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': f'{api.base_url}/action/Assignees',
        }
        
        print('🔍 Fetching assignees page...')
        r = api.session.get(url, headers=headers, timeout=20)
        
        print(f'Status: {r.status_code}')
        print(f'Content length: {len(r.text)}')
        
        # Save the full HTML
        with open('debug_assignees_full.html', 'w', encoding='utf-8') as f:
            f.write(r.text)
        print('💾 Saved full HTML to debug_assignees_full.html')
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Look for different patterns
        print('\n🔍 Looking for li.client.assignee elements...')
        assignee_li = soup.find_all('li', class_='client assignee')
        print(f'Found {len(assignee_li)} li.client.assignee elements')
        
        # Show first few
        for i, li in enumerate(assignee_li[:3]):
            onclick = li.get('onclick', '')
            text = li.get_text(strip=True)[:100]
            print(f'  {i+1}. onclick="{onclick}" text="{text}"')
        
        print('\n🔍 Looking for any li with client class...')
        client_li = soup.find_all('li', class_='client')
        print(f'Found {len(client_li)} li.client elements')
        
        print('\n🔍 Looking for any li with assignee class...')
        assignee_li_all = soup.find_all('li', class_='assignee')
        print(f'Found {len(assignee_li_all)} li.assignee elements')
        
        print('\n🔍 Looking for onclick delegate patterns...')
        delegate_elements = soup.select('[onclick*="delegate("]')
        print(f'Found {len(delegate_elements)} elements with delegate onclick')
        
        # Show first few
        for i, element in enumerate(delegate_elements[:5]):
            onclick = element.get('onclick', '')
            text = element.get_text(strip=True)[:50]
            print(f'  {i+1}. {element.name} onclick="{onclick}" text="{text}"')
        
        # Try regex on raw HTML
        print('\n🔍 Using regex on raw HTML...')
        delegate_matches = re.findall(r'delegate\((\d+),', r.text)
        print(f'Found {len(delegate_matches)} delegate matches: {delegate_matches[:10]}')
        
    else:
        print('❌ Authentication failed')

if __name__ == "__main__":
    debug_assignees_html()