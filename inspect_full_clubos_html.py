"""
Inspect the FULL HTML structure from ClubOS messages to find timestamps
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.clubos_messaging_client_simple import ClubOSMessagingClient
from config.secrets import get_clubos_credentials
import logging

CLUBOS_CREDENTIALS = get_clubos_credentials()

# Enable detailed logging
logging.basicConfig(level=logging.INFO)

# Initialize client
print("🔐 Initializing ClubOS client...")
client = ClubOSMessagingClient(CLUBOS_CREDENTIALS)

# Authenticate automatically by calling get_messages
print("\n� Fetching messages from ClubOS (authentication happens automatically)...")

# Use the _ensure_authenticated_session method to get the session
if not client.authenticate():
    print("❌ Authentication failed")
    sys.exit(1)

print("✅ Authentication successful")

# Now make a direct request to get the RAW HTML
messages_url = f"{client.base_url}/action/Dashboard/messages"
headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept": "text/html, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{client.base_url}/action/Dashboard/view",
    "Origin": client.base_url,
    "User-Agent": client.session.headers.get('User-Agent', 'Mozilla/5.0')
}

# Get messages for a sample owner
post_data = {
    "userId": ""  # Empty to get all messages
}

print(f"\n🔄 POST to {messages_url}...")
response = client.session.post(
    messages_url, 
    data=post_data, 
    headers=headers, 
    timeout=30,
    allow_redirects=False,
    verify=False
)

if response.status_code == 200:
    html_content = response.text
    
    # Save full HTML to file for inspection
    with open('clubos_messages_full_html.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Saved full HTML to clubos_messages_full_html.html ({len(html_content)} bytes)")
    
    # Print first 10,000 characters to see structure
    print("\n" + "="*80)
    print("FIRST 10,000 CHARACTERS OF HTML:")
    print("="*80)
    print(html_content[:10000])
    print("\n" + "="*80)
    
    # Find all elements that might contain timestamps
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print("\n🔍 LOOKING FOR TIMESTAMP-RELATED ELEMENTS:")
    print("="*80)
    
    # Check for any elements with 'time', 'date', 'timestamp' in class or id
    time_elements = soup.find_all(lambda tag: tag.has_attr('class') and 
                                   any('time' in str(c).lower() or 'date' in str(c).lower() 
                                       for c in tag.get('class', [])))
    
    if time_elements:
        print(f"\n✅ Found {len(time_elements)} elements with 'time' or 'date' in class:")
        for i, elem in enumerate(time_elements[:5]):  # First 5
            print(f"\n--- Element {i+1} ---")
            print(f"Tag: {elem.name}")
            print(f"Attributes: {elem.attrs}")
            print(f"Content: {elem.get_text(strip=True)[:200]}")
            print(f"HTML: {str(elem)[:500]}")
    else:
        print("❌ No elements with 'time' or 'date' in class names")
    
    # Check for any data-* attributes that might contain timestamps
    print("\n🔍 LOOKING FOR DATA-* ATTRIBUTES:")
    print("="*80)
    
    elements_with_data = soup.find_all(lambda tag: any(attr.startswith('data-') for attr in tag.attrs.keys()))
    
    if elements_with_data:
        print(f"\n✅ Found {len(elements_with_data)} elements with data-* attributes:")
        for i, elem in enumerate(elements_with_data[:10]):  # First 10
            data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
            if data_attrs:
                print(f"\n--- Element {i+1} ---")
                print(f"Tag: {elem.name}")
                print(f"Data attributes: {data_attrs}")
                print(f"Content: {elem.get_text(strip=True)[:100]}")
    else:
        print("❌ No elements with data-* attributes")
    
    # Look at the ACTUAL structure of message elements
    print("\n🔍 ACTUAL MESSAGE ELEMENT STRUCTURE (First 3 messages):")
    print("="*80)
    
    message_divs = soup.find_all('div', class_='message')
    if message_divs:
        for i, msg_div in enumerate(message_divs[:3]):
            print(f"\n{'='*60}")
            print(f"MESSAGE {i+1} - COMPLETE HTML STRUCTURE:")
            print(f"{'='*60}")
            print(str(msg_div))
            print(f"\n{'='*60}")
            print(f"MESSAGE {i+1} - PARENT ELEMENT:")
            print(f"{'='*60}")
            if msg_div.parent:
                print(f"Parent tag: {msg_div.parent.name}")
                print(f"Parent attributes: {msg_div.parent.attrs}")
                print(f"Parent HTML (first 1000 chars):")
                print(str(msg_div.parent)[:1000])
    else:
        print("❌ No div.message elements found")
        
        # Try to find messages with a broader search
        print("\n🔍 Searching for ANY elements containing 'Jan' or 'Feb' (date indicators):")
        date_elements = soup.find_all(string=lambda text: text and ('Jan' in text or 'Feb' in text or 'Mar' in text))
        
        if date_elements:
            print(f"\n✅ Found {len(date_elements)} text nodes with dates:")
            for i, text_node in enumerate(date_elements[:5]):
                parent = text_node.parent
                print(f"\n--- Date Node {i+1} ---")
                print(f"Text: {text_node.strip()}")
                print(f"Parent tag: {parent.name}")
                print(f"Parent attributes: {parent.attrs}")
                print(f"Parent HTML: {str(parent)[:500]}")
                
                # Show grandparent too
                if parent.parent:
                    print(f"Grandparent tag: {parent.parent.name}")
                    print(f"Grandparent attributes: {parent.parent.attrs}")
        else:
            print("❌ No date text found")

else:
    print(f"❌ Failed to fetch messages: {response.status_code}")
    print(response.text[:1000])
