#!/usr/bin/env python3
"""
Analyze ClubOS HTML structure to identify the correct message containers
"""

import requests
from bs4 import BeautifulSoup

def analyze_clubos_structure():
    """Analyze the HTML structure to find message containers"""
    
    # Make actual API call
    url = "https://anytime.club-os.com/action/FollowUp"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqZXJlbXkuYXJtc3Ryb25nQGFudGhlbS1maXRuZXNzLmNvbSIsImlhdCI6MTczNDkxMzc4MCwiZXhwIjoxNzM0OTU2OTgwfQ.Q-7NWpNOMEwHCpGKDLi6CejPiEBnJpbPr6YnFE7pYBM'
    }
    
    cookies = {
        'club_id': '153',
        '_ga': 'GA1.1.1476905969.1734828652',
        '_ga_4T47KNNLQG': 'GS1.1.1734913797.3.0.1734913797.0.0.0'
    }
    
    params = {
        'followUpUserId': '191015549',  # Grace Sphatt's ID
        'followUpType': '3'  # Message history
    }
    
    print("🚀 Making ClubOS FollowUp API request...")
    response = requests.get(url, headers=headers, cookies=cookies, params=params)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"📏 Response Length: {len(response.text)} characters")
        
        # Look for all div elements with classes
        all_divs_with_class = soup.find_all('div', class_=True)
        
        # Get unique class names
        class_names = set()
        for div in all_divs_with_class:
            classes = div.get('class', [])
            for cls in classes:
                if 'follow' in cls.lower() or 'entry' in cls.lower() or 'message' in cls.lower():
                    class_names.add(cls)
        
        print(f"\n🔍 Found relevant CSS classes:")
        for cls in sorted(class_names):
            print(f"   - {cls}")
        
        # Look for divs containing date patterns
        import re
        date_pattern = re.compile(r'\d{1,2}/\d{1,2}/\d{2,4}')
        
        divs_with_dates = []
        for div in soup.find_all('div'):
            text = div.get_text(strip=True)
            if date_pattern.search(text) and len(text) < 200:  # Likely date header
                divs_with_dates.append({
                    'class': div.get('class', []),
                    'text': text[:100],
                    'parent_class': div.parent.get('class', []) if div.parent else []
                })
        
        print(f"\n📅 Found {len(divs_with_dates)} divs containing dates:")
        for i, div_info in enumerate(divs_with_dates[:10]):  # Show first 10
            print(f"   {i+1}. Class: {div_info['class']} | Parent: {div_info['parent_class']}")
            print(f"      Text: {div_info['text']}")
        
        # Look for specific patterns we saw in the previous sample
        sample_text_patterns = [
            "9/25/25 @ 05:13 PM by Grace S.",
            "Text - Left Message -",
            "Email -",
            "CONFIRM"
        ]
        
        for pattern in sample_text_patterns:
            matches = soup.find_all(text=re.compile(re.escape(pattern), re.IGNORECASE))
            if matches:
                print(f"\n🎯 Found pattern '{pattern}': {len(matches)} matches")
                for match in matches[:3]:  # Show first 3
                    parent = match.parent
                    print(f"   Parent tag: {parent.name}, Class: {parent.get('class', [])}")
        
        # Save a snippet of HTML for manual analysis
        with open('clubos_html_sample.html', 'w', encoding='utf-8') as f:
            f.write(response.text[:50000])  # First 50k characters
        
        print(f"\n💾 Saved HTML sample to clubos_html_sample.html")
        
    else:
        print(f"❌ API request failed with status {response.status_code}")

if __name__ == "__main__":
    analyze_clubos_structure()