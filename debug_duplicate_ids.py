#!/usr/bin/env python3
"""Debug script to check message IDs"""
import sys
sys.path.insert(0, '.')
from src.services.clubos_messaging_client_simple import ClubOSMessagingClient

client = ClubOSMessagingClient()
client.authenticate()
msgs = client.get_messages('187032782')

print(f"Total messages: {len(msgs)}")
print("\nFirst 10 ClubOS IDs:")
for m in msgs[:10]:
    print(f"  {m.get('id')}")

# Check unique IDs
ids = [m.get('id') for m in msgs]
unique_ids = set(ids)
print(f"\nUnique: {len(unique_ids)} vs Total: {len(ids)}")
