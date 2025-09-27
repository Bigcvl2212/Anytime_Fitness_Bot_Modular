#!/usr/bin/env python3
"""
Test ClubOS FollowUp response parsing with actual API data
"""

import os
import sys
import requests
import json

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Import BeautifulSoup for HTML parsing
try:
    from bs4 import BeautifulSoup
    bs4_available = True
except ImportError:
    print("⚠️ BeautifulSoup4 not available, installing...")
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'beautifulsoup4', 'lxml'])
    from bs4 import BeautifulSoup
    bs4_available = True

# Define the parsing function directly here to avoid import issues
def parse_clubos_followup_response(html_content: str, member_id: str) -> list:
    """Parse ClubOS FollowUp HTML response to extract message history"""
    try:
        import re
        from datetime import datetime
        
        soup = BeautifulSoup(html_content, 'html.parser')
        messages = []
        
        # Look for followup-entry divs which contain the message history
        followup_entries = soup.find_all('div', class_='followup-entry')
        
        print(f"🔍 Found {len(followup_entries)} followup entries in ClubOS response")
        
        for entry in followup_entries:
            try:
                # Extract date and author from followup-entry-date
                date_div = entry.find('div', class_='followup-entry-date')
                note_div = entry.find('div', class_='followup-entry-note')
                
                if not date_div or not note_div:
                    continue
                
                date_text = date_div.get_text(strip=True)
                note_text = note_div.get_text(strip=True)
                
                # Skip empty entries
                if len(note_text.strip()) < 5:
                    continue
                
                # Parse date and author from date_text (format: "9/25/25 @ 05:13 PM by Grace S.")
                timestamp = None
                author = 'Unknown'
                
                # Extract date and time
                date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})\s*@\s*(\d{1,2}:\d{2}\s*[AP]M)', date_text)
                if date_match:
                    date_str = date_match.group(1)
                    time_str = date_match.group(2)
                    
                    # Convert to full year format
                    if '/' in date_str:
                        date_parts = date_str.split('/')
                        if len(date_parts[2]) == 2:  # Convert YY to YYYY
                            year = int(date_parts[2])
                            if year > 50:
                                date_parts[2] = f"19{year}"
                            else:
                                date_parts[2] = f"20{year}"
                        date_str = '/'.join(date_parts)
                    
                    timestamp = f"{date_str} {time_str}"
                
                # Extract author (format: "by Grace S." or "by Jeremy M.")
                author_match = re.search(r'by\s+([^.]+\.?)', date_text)
                if author_match:
                    author = author_match.group(1).strip()
                
                # Determine message type based on content and images
                message_type = 'conversation'
                status = 'received'
                
                # Check for message type indicators
                if 'icon_text.png' in str(note_div):
                    message_type = 'sms'
                elif 'icon_email.png' in str(note_div):
                    message_type = 'email'
                elif 'icon_phone.png' in str(note_div):
                    message_type = 'call'
                
                # Check for sent vs received (staff names vs member confirmations)
                staff_indicators = ['Jeremy M.', 'Natoya T.', 'by Jeremy', 'by Staff', 'Gym Bot']
                if any(indicator in date_text for indicator in staff_indicators) or 'Message sent via' in note_text:
                    status = 'sent'
                elif 'CONFIRM' in note_text or 'confirmed' in note_text.lower():
                    status = 'received'
                
                # Clean up the message content
                content = note_text
                
                # Remove image references and clean up
                content = re.sub(r'Text - Left Message - ', '', content)
                content = re.sub(r'Email - ', '', content)
                content = re.sub(r'Call - ', '', content)
                
                message_data = {
                    'id': f"clubos_followup_{member_id}_{hash(content + str(timestamp)) % 1000000}",
                    'member_id': member_id,
                    'content': content[:1000],  # Limit content length
                    'timestamp': timestamp or datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                    'created_at': timestamp or datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                    'message_type': message_type,
                    'status': status,
                    'from_user': author,
                    'to_user': 'Grace Sphatt' if status == 'sent' else author,  # Member name from header
                    'source': 'clubos_followup',
                    'channel': 'clubos'
                }
                
                messages.append(message_data)
                
            except Exception as entry_error:
                print(f"⚠️ Error parsing followup entry: {entry_error}")
                continue
        
        # Sort messages by timestamp (newest first)
        messages.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        print(f"✅ Successfully parsed {len(messages)} messages from ClubOS FollowUp response for member {member_id}")
        return messages
        
    except Exception as e:
        print(f"❌ Error parsing ClubOS FollowUp response: {e}")
        return []
import requests
import json

def test_actual_clubos_parsing():
    """Test the parsing function with real ClubOS data"""
    
    # Make actual API call to get real data
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
    
    print(f"📊 API Response Status: {response.status_code}")
    print(f"📏 Response Length: {len(response.text)} characters")
    
    if response.status_code == 200:
        print("\n🔍 Testing message parsing...")
        
        # Parse the messages
        messages = parse_clubos_followup_response(response.text, '191015549')
        
        print(f"✅ Successfully parsed {len(messages)} messages!")
        
        # Display first few messages
        for i, msg in enumerate(messages[:5]):  # Show first 5 messages
            print(f"\n📨 Message #{i+1}:")
            print(f"   📅 Timestamp: {msg.get('timestamp')}")
            print(f"   👤 From: {msg.get('from_user')}")
            print(f"   📱 Type: {msg.get('message_type')} ({msg.get('status')})")
            print(f"   💬 Content: {msg.get('content')[:100]}{'...' if len(msg.get('content', '')) > 100 else ''}")
        
        # Save sample for analysis
        if messages:
            with open('sample_parsed_messages.json', 'w') as f:
                json.dump(messages[:10], f, indent=2)
            print(f"\n💾 Saved first 10 parsed messages to sample_parsed_messages.json")
        
        return messages
    else:
        print(f"❌ API request failed with status {response.status_code}")
        return []

if __name__ == "__main__":
    test_actual_clubos_parsing()
