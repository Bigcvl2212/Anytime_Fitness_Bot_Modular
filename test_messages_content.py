import requests
import json
import re

# Get messages from API
response = requests.get('http://localhost:5000/api/messages')
data = response.json()
messages = data.get('messages', [])

print(f"Total messages: {len(messages)}")
print("\n" + "="*50)
print("SAMPLE MESSAGES:")
print("="*50)

# Show first 5 messages
for i, message in enumerate(messages[:5]):
    print(f"\nMessage {i+1}:")
    print(f"Content: {message.get('content', 'No content')}")
    print(f"From User: {message.get('from_user', 'No from_user')}")
    print(f"Member ID: {message.get('member_id', 'No member_id')}")
    print(f"Timestamp: {message.get('timestamp', 'No timestamp')}")
    print("-" * 30)

print("\n" + "="*50)
print("NAME EXTRACTION TEST:")
print("="*50)

# Test name extraction on first few messages
for i, message in enumerate(messages[:3]):
    content = message.get('content', '')
    print(f"\nMessage {i+1} content: {content[:100]}...")
    
    # Simple Python name extraction test
    if content:
        # Look for name pattern at the beginning
        name_match = re.match(r'^([A-Z][a-z]+ [A-Z][a-z]+)', content)
        if name_match:
            name = name_match.group(1)
            print(f"  Extracted name: {name}")
        else:
            print(f"  No name found at beginning")
            
        # Look for any name pattern in content
        name_pattern = r'([A-Z][a-z]+ [A-Z][a-z]+)'
        matches = re.findall(name_pattern, content)
        if matches:
            print(f"  All name matches: {matches}")
        else:
            print(f"  No name patterns found")
