#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sync fresh messages from ClubOS and analyze the raw data structure
"""
import sys
import os

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.clubos_messaging_client_simple import ClubOSMessagingClient
import json

# Get credentials from environment
from dotenv import load_dotenv
load_dotenv()

username = os.getenv('CLUBOS_USERNAME')
password = os.getenv('CLUBOS_PASSWORD')

if not username or not password:
    print("❌ No credentials found in environment")
    sys.exit(1)

print("🔐 Authenticating with ClubOS...")
client = ClubOSMessagingClient(
    username=username,
    password=password
)

if not client.authenticate():
    print("❌ Authentication failed")
    sys.exit(1)

print("✅ Authenticated! Fetching messages...")
messages = client.get_messages('187032782')

print(f"\n📊 Got {len(messages)} messages")
print("\n" + "="*80)
print("ANALYZING FIRST 5 MESSAGES (RAW DATA):")
print("="*80)

for i, msg in enumerate(messages[:5], 1):
    print(f"\nMessage {i}:")
    print(f"  From: {msg.get('from_user', 'Unknown')}")
    print(f"  Timestamp: {msg.get('timestamp', 'No timestamp')}")
    print(f"  Content: {msg.get('content', '')[:100]}...")
    print(f"  Raw keys: {list(msg.keys())}")
    print(f"  Full message data: {json.dumps(msg, indent=2)}")

print("\n" + "="*80)
print("Check if messages have any hidden timestamp fields or data attributes")
print("="*80)
