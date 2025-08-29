#!/usr/bin/env python3
"""
Test the updated ClubHub API client with exact working parameters
"""

import sys
import os
sys.path.append('src/services')
from api.clubhub_api_client import ClubHubAPIClient
sys.path.append('src/config')
from clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

print('🚀 Testing FIXED prospects API with EXACT parameters from working script...')
client = ClubHubAPIClient()
if client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
    print('✅ ClubHub authenticated - fetching ALL prospects with working parameters...')
    prospects = client.get_all_prospects_paginated()
    print(f'🎯 RESULT: Got {len(prospects)} total prospects!')
    if prospects:
        first = prospects[0]
        name = f"{first.get('firstName', '')} {first.get('lastName', '')}".strip()
        email = first.get('email', '')
        print(f'📋 First prospect: {name} - {email}')
        print(f'🔑 First prospect keys: {list(first.keys())}')
else:
    print('❌ ClubHub authentication failed')
