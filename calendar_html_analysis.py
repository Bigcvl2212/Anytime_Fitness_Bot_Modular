#!/usr/bin/env python3
"""
Extract calendar data from the HTML page directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clubos_integration_fixed import RobustClubOSClient
import re
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_calendar_data_from_html():
    """Extract calendar data directly from the calendar page HTML"""
    
    # Load credentials
    try:
        from config.secrets_local import get_secret
        CLUBOS_USERNAME = get_secret("clubos-username")
        CLUBOS_PASSWORD = get_secret("clubos-password")
        
        if not CLUBOS_USERNAME or not CLUBOS_PASSWORD:
            print("❌ Could not load ClubOS credentials")
            return
    except ImportError:
        print("❌ Could not load credentials from config.secrets_local")
        return
    
    print("=== Extracting Calendar Data from HTML ===")
    
    # Initialize client with working authentication
    client = RobustClubOSClient(CLUBOS_USERNAME, CLUBOS_PASSWORD)
    
    # Authenticate
    print("🔐 Authenticating with ClubOS...")
    if not client.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful!")
    
    # Get calendar page HTML
    print("📅 Loading calendar page...")
    calendar_url = f"{client.base_url}/action/Calendar"
    response = client.session.get(calendar_url)
    
    if not response.ok:
        print(f"❌ Failed to load calendar page: {response.status_code}")
        return
    
    html_content = response.text
    print(f"📄 Calendar page loaded ({len(html_content)} characters)")
    
    # Look for JavaScript variables with calendar data
    print("\n=== Searching for Calendar Data in JavaScript ===")
    
    # Common patterns for calendar data
    patterns = [
        r'var\s+events\s*=\s*(\[.*?\]);',
        r'events\s*:\s*(\[.*?\])',
        r'calendar.*?data\s*:\s*(\{.*?\})',
        r'calendar.*?events\s*:\s*(\[.*?\])',
        r'"events"\s*:\s*(\[.*?\])',
        r'eventData\s*=\s*(\[.*?\]);',
        r'calendarEvents\s*=\s*(\[.*?\]);'
    ]
    
    for i, pattern in enumerate(patterns):
        matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
        if matches:
            print(f"Pattern {i+1} found {len(matches)} matches:")
            for j, match in enumerate(matches[:3]):  # Show first 3
                try:
                    # Try to parse as JSON
                    data = json.loads(match)
                    print(f"  Match {j+1}: Valid JSON with {len(data) if isinstance(data, (list, dict)) else 'unknown'} items")
                    if isinstance(data, list) and len(data) > 0:
                        print(f"    First item: {str(data[0])[:100]}...")
                    elif isinstance(data, dict):
                        print(f"    Keys: {list(data.keys())[:5]}")
                except:
                    print(f"  Match {j+1}: {match[:100]}...")
    
    # Look for AJAX endpoints in JavaScript
    print("\n=== Searching for AJAX Endpoints ===")
    ajax_patterns = [
        r'ajax\([\'"]([^\'"]+)[\'"]',
        r'\.get\([\'"]([^\'"]+)[\'"]',
        r'\.post\([\'"]([^\'"]+)[\'"]',
        r'url\s*:\s*[\'"]([^\'"]+)[\'"]',
        r'endpoint\s*:\s*[\'"]([^\'"]+)[\'"]'
    ]
    
    endpoints = set()
    for pattern in ajax_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            if 'calendar' in match.lower() or 'event' in match.lower():
                endpoints.add(match)
    
    if endpoints:
        print("Found potential calendar endpoints:")
        for endpoint in sorted(endpoints):
            print(f"  {endpoint}")
    
    # Look for form data that might be needed for API calls
    print("\n=== Searching for Form Data ===")
    form_patterns = [
        r'<input[^>]*name=[\'"]([^\'"]+)[\'"][^>]*value=[\'"]([^\'"]+)[\'"]',
        r'data-[a-zA-Z-]+=[\'"]([^\'"]+)[\'"]'
    ]
    
    form_data = {}
    for pattern in form_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for name, value in matches[:10]:  # First 10 matches
            if any(keyword in name.lower() for keyword in ['token', 'csrf', 'session', 'auth']):
                form_data[name] = value[:20] + '...' if len(value) > 20 else value
    
    if form_data:
        print("Found potential authentication form data:")
        for name, value in form_data.items():
            print(f"  {name}: {value}")
    
    # Look for calendar configuration
    print("\n=== Searching for Calendar Configuration ===")
    config_patterns = [
        r'calendar.*?config\s*:\s*(\{[^}]+\})',
        r'apiUrl\s*:\s*[\'"]([^\'"]+)[\'"]',
        r'baseUrl\s*:\s*[\'"]([^\'"]+)[\'"]'
    ]
    
    for pattern in config_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        if matches:
            print(f"Config pattern matches: {matches[:3]}")
    
    print("\n✅ Calendar HTML analysis complete!")

if __name__ == "__main__":
    extract_calendar_data_from_html()
