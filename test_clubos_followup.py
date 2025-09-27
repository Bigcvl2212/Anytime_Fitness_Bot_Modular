#!/usr/bin/env python3
"""
Test ClubOS FollowUp API integration for member message history
"""

import requests
import json
from datetime import datetime

def test_clubos_followup_api():
    """Test the ClubOS FollowUp API with your exact curl parameters"""
    
    # Your exact curl parameters
    url = "https://anytime.club-os.com/action/FollowUp"
    
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg1Nzc3Mjc2LCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiIwOUFFNjlFNjAwNDk4M0Q5Q0NFQzYwMDk0NEM1OTA3MCJ9.qavP5IKfXB_0wZ6HY3CXZ-C51E-BjbD6gwzECkOuMH4',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://anytime.club-os.com',
        'referer': 'https://anytime.club-os.com/action/Dashboard/view',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    # Convert cookie string to dictionary
    cookies_str = '_fbp=fb.1.1750181614288.28580080925040380; __ecatft={"utm_campaign":"","utm_source":"","utm_medium":"","utm_content":"","utm_term":"","utm_device":"","referrer":"https://www.bing.com/","gclid":"","lp":"www.club-os.com/"}; osano_consentmanager_uuid=87bca4d8-cdaa-4638-9c0a-e6e1bc9a4c28; loggedInUserId=187032782; _gid=GA1.2.972902625.1758503773; JSESSIONID=09AE69E6004983D9CCEC600944C59070'
    
    cookies = {}
    for cookie in cookies_str.split('; '):
        if '=' in cookie:
            key, value = cookie.split('=', 1)
            cookies[key] = value
    
    # Test with the member ID from your example
    test_member_id = '185777276'
    
    data = {
        'followUpUserId': test_member_id,
        'followUpType': '3'  # Type 3 for messages
    }
    
    print(f"🧪 Testing ClubOS FollowUp API for member {test_member_id}")
    print(f"📡 URL: {url}")
    print(f"📝 Data: {data}")
    
    try:
        response = requests.post(
            url,
            headers=headers,
            cookies=cookies,
            data=data,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📏 Response Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            print("✅ ClubOS FollowUp API request successful!")
            
            # Save the response for analysis
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'clubos_followup_test_response_{timestamp}.html'
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"💾 Response saved to: {filename}")
            
            # Basic analysis of the response
            html_content = response.text.lower()
            
            indicators = {
                'messages': ['message', 'conversation', 'text', 'sms', 'email'],
                'dates': ['date', 'time', 'created', 'sent', 'received'],
                'tables': ['<table', '<tr', '<td'],
                'forms': ['<form', 'input', 'textarea'],
                'member_info': ['member', 'user', 'profile', 'contact']
            }
            
            print("\n📋 Response Content Analysis:")
            for category, keywords in indicators.items():
                count = sum(html_content.count(keyword) for keyword in keywords)
                print(f"  {category.title()}: {count} occurrences")
            
            # Look for specific patterns
            if 'message' in html_content and ('table' in html_content or 'tr' in html_content):
                print("🎯 Response likely contains message history in table format")
            
            if 'no' in html_content and ('message' in html_content or 'record' in html_content):
                print("📭 Response might indicate no messages found")
            
        else:
            print(f"❌ ClubOS FollowUp API request failed: {response.status_code}")
            print(f"📄 Response: {response.text[:500]}...")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 30 seconds")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - check network connectivity")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")

if __name__ == "__main__":
    test_clubos_followup_api()