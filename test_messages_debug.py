import requests

# Test the messages API
response = requests.get('http://localhost:5000/api/messages?limit=3')
data = response.json()

print("Sample messages:")
for i, msg in enumerate(data.get('messages', [])[:3]):
    print(f"\n--- Message {i+1} ---")
    print(f"Content: {msg.get('content', 'No content')}")
    print(f"From: {msg.get('from_user', 'No from')}")
    print(f"Member ID: {msg.get('member_id', 'No member_id')}")
    print(f"Timestamp: {msg.get('timestamp', 'No timestamp')}")
