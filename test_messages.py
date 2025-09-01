import requests

# Test the messages API
response = requests.get('http://localhost:5000/api/messages?limit=5')
data = response.json()

print(f"Status: {response.status_code}")
print(f"Messages found: {len(data.get('messages', []))}")

# Show first 3 messages with timestamps
for i, msg in enumerate(data.get('messages', [])[:3]):
    timestamp = msg.get('timestamp', 'No time')
    content = msg.get('content', 'No content')[:50]
    print(f"  {i+1}. {timestamp} - {content}...")

# Test the messages page
page_response = requests.get('http://localhost:5000/messaging')
print(f"\nMessages page status: {page_response.status_code}")
