#!/usr/bin/env python3
"""
Test script to analyze the structure of ClubOS FollowUp API response
"""
import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_clubos_followup(member_id="149169"):
    """Test the ClubOS FollowUp API with the provided authentication"""
    
    url = "https://anytime.club-os.com/action/FollowUp"
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczNzc0NDc5OCwiaWF0IjoxNzM3MTE2Nzk4LCJqdGkiOiI4OGYzMjc0MS03M2I2LTRhZTktOTk1My05MjdkNDM0ODY0NGMifQ.0MnRvmhmzQwvBHOTm7nHKhqkZPTi3q3cgBn5lFT1MtE',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': 'JSESSIONID=3D7E25157DCDA45FF0E28F3A5F80B3C0; mplvl=; location=; tmr_lvid=2dc7d58cf8a35b7a59c5c46adeac5b27; tmr_lvidTS=1737116790778; tmr_reqNum=3; _ga=GA1.1.1985012089.1737116791; _ga_4D1X4YVPG7=GS1.1.1737116791.1.1.1737116848.3.0.0',
        'origin': 'https://anytime.club-os.com',
        'referer': 'https://anytime.club-os.com/action/Prospects',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    data = {
        'followUpUserId': member_id,
        'followUpType': '3'
    }
    
    try:
        print(f"📡 Testing ClubOS FollowUp API for member {member_id}...")
        response = requests.post(url, headers=headers, data=data)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📄 Response length: {len(response.text)} characters")
        print(f"📑 Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        # Save full response
        with open(f"clubos_response_{member_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html", 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Analyze content structure
        print("\n🔍 CONTENT ANALYSIS:")
        content = response.text
        
        # Check if it's HTML, JSON, or JavaScript
        if content.strip().startswith('<'):
            print("   Format: HTML")
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check for common ClubOS classes
            followup_entries = soup.find_all('div', class_='followup-entry')
            print(f"   followup-entry divs: {len(followup_entries)}")
            
            system_messages = soup.find_all(class_='system-message')
            print(f"   system-message elements: {len(system_messages)}")
            
            # Look for date patterns
            date_pattern = re.compile(r'\d{1,2}/\d{1,2}/\d{2,4}\s*[@at]\s*\d{1,2}:\d{2}\s*[AP]M', re.IGNORECASE)
            date_matches = date_pattern.findall(content)
            print(f"   Date patterns found: {len(date_matches)}")
            if date_matches:
                print(f"   Sample dates: {date_matches[:3]}")
            
            # Look for common text indicators
            text_indicators = ['Text -', 'Email -', 'Call -', 'by Jeremy', 'by Grace', 'by Staff']
            for indicator in text_indicators:
                count = content.count(indicator)
                if count > 0:
                    print(f"   '{indicator}': {count} occurrences")
            
            # Check for table structures
            tables = soup.find_all('table')
            print(f"   Tables found: {len(tables)}")
            
            # Check for any divs with meaningful content
            all_divs = soup.find_all('div')
            text_divs = [div for div in all_divs if div.get_text(strip=True) and len(div.get_text(strip=True)) > 10]
            print(f"   Divs with text content: {len(text_divs)}")
            
        elif content.strip().startswith('{') or content.strip().startswith('['):
            print("   Format: JSON")
            try:
                json_data = json.loads(content)
                print(f"   JSON keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'Array'}")
            except:
                print("   JSON parsing failed")
                
        else:
            print("   Format: Unknown/JavaScript")
            
        # Show first 500 characters
        print(f"\n📝 FIRST 500 CHARACTERS:")
        print(content[:500])
        print("...")
        
        # Show last 200 characters  
        print(f"\n📝 LAST 200 CHARACTERS:")
        print("...")
        print(content[-200:])
        
        return response.text
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    member_id = input("Enter member ID (default: 149169): ").strip() or "149169"
    result = test_clubos_followup(member_id)
    
    if result:
        print(f"\n✅ Test completed. Response saved to file.")
    else:
        print(f"\n❌ Test failed.")