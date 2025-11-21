import requests
import time

print("Testing inbox speed...")
start = time.time()
r = requests.get('http://localhost:5000/api/messaging/inbox/recent?limit=15')
elapsed = time.time() - start

data = r.json()
print(f"\n✅ Response time: {elapsed:.2f} seconds")
print(f"✅ Messages returned: {len(data.get('messages', []))}")
print(f"\nFirst 3 messages:")
for msg in data.get('messages', [])[:3]:
    print(f"  - {msg['member_name']}: {msg['message_content'][:50]}...")
