#!/usr/bin/env python3
"""
Analyze ClubOS calendar HTML structure and extract real calendar data
"""
import sys
import os
import re
from bs4 import BeautifulSoup

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from services.api.clubos_api_client import ClubOSAPIClient, ClubOSAPIAuthentication
from config.secrets_local import get_secret

def analyze_calendar_html():
    """Analyze the ClubOS calendar HTML to understand its structure"""
    
    # Initialize client and authenticate
    auth_service = ClubOSAPIAuthentication()
    client = ClubOSAPIClient(auth_service)
    print("[INFO] Authenticating with ClubOS...")
    
    if not auth_service.login(get_secret('clubos-username'), get_secret('clubos-password')):
        print("[ERROR] Authentication failed")
        return
    
    print("[INFO] Authentication successful")
    
    # Fetch calendar HTML
    calendar_url = f"{client.base_url}/action/Calendar"
    print(f"[INFO] Fetching calendar from: {calendar_url}")
    
    response = client.session.get(calendar_url)
    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch calendar page: {response.status_code}")
        return
    
    html_content = response.text
    print(f"[INFO] Fetched {len(html_content)} characters of HTML")
    
    # Save full HTML for debugging
    with open('clubos_calendar_full.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("[INFO] Saved full HTML to clubos_calendar_full.html")
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for various calendar-related patterns
    patterns_to_search = [
        # Common calendar class names
        r'calendar',
        r'schedule',
        r'appointment',
        r'event',
        r'session',
        r'slot',
        r'booking',
        r'time',
        
        # Time patterns
        r'\d{1,2}:\d{2}\s*[AaPp][Mm]',
        r'\d{1,2}:\d{2}',
        
        # Date patterns
        r'\d{1,2}/\d{1,2}/\d{4}',
        r'\d{4}-\d{2}-\d{2}',
        
        # Common scheduling terms
        r'available',
        r'trainer',
        r'instructor',
        r'class',
        r'workout'
    ]
    
    print("\n[ANALYSIS] Searching for calendar-related content...")
    
    # Search for elements with calendar-related attributes
    calendar_elements = []
    for tag in soup.find_all():
        if tag.get('class'):
            classes = ' '.join(tag.get('class', []))
            if any(pattern in classes.lower() for pattern in ['calendar', 'schedule', 'appointment', 'event', 'session', 'slot', 'booking']):
                calendar_elements.append({
                    'tag': tag.name,
                    'classes': classes,
                    'id': tag.get('id', ''),
                    'text': tag.get_text().strip()[:100]  # First 100 chars
                })
        
        if tag.get('id'):
            id_attr = tag.get('id', '')
            if any(pattern in id_attr.lower() for pattern in ['calendar', 'schedule', 'appointment', 'event', 'session', 'slot', 'booking']):
                calendar_elements.append({
                    'tag': tag.name,
                    'classes': ' '.join(tag.get('class', [])),
                    'id': id_attr,
                    'text': tag.get_text().strip()[:100]
                })
    
    print(f"[ANALYSIS] Found {len(calendar_elements)} potential calendar elements:")
    for i, elem in enumerate(calendar_elements[:10]):  # Show first 10
        print(f"  {i+1}. <{elem['tag']} class='{elem['classes']}' id='{elem['id']}'>{elem['text'][:50]}...")
    
    # Search for time patterns in text
    time_patterns = re.findall(r'\d{1,2}:\d{2}\s*[AaPp][Mm]|\d{1,2}:\d{2}', html_content, re.IGNORECASE)
    print(f"\n[ANALYSIS] Found {len(time_patterns)} time patterns:")
    unique_times = list(set(time_patterns))[:20]  # Show first 20 unique
    for time_pattern in unique_times:
        print(f"  - {time_pattern}")
    
    # Look for JavaScript that might load calendar data
    script_tags = soup.find_all('script')
    print(f"\n[ANALYSIS] Found {len(script_tags)} script tags")
    
    # Search for AJAX/API calls in JavaScript
    api_patterns = []
    for script in script_tags:
        if script.string:
            # Look for API endpoints
            api_matches = re.findall(r'["\']/?api/[^"\']*["\']', script.string)
            api_patterns.extend(api_matches)
            
            # Look for AJAX calls
            ajax_matches = re.findall(r'\.ajax\s*\(|fetch\s*\(|XMLHttpRequest', script.string)
            if ajax_matches:
                print(f"  [JS] Found AJAX/fetch calls in script")
    
    unique_apis = list(set(api_patterns))
    if unique_apis:
        print(f"[ANALYSIS] Found {len(unique_apis)} potential API endpoints:")
        for api in unique_apis[:10]:
            print(f"  - {api}")
    
    # Look for data attributes that might contain calendar info
    data_elements = []
    for tag in soup.find_all():
        if hasattr(tag, 'attrs') and tag.attrs:
            data_attrs = {k: v for k, v in tag.attrs.items() if k.startswith('data-')}
            if data_attrs:
                data_elements.append({
                    'tag': tag.name,
                    'data_attrs': data_attrs,
                    'text': tag.get_text().strip()[:50]
                })
    
    print(f"\n[ANALYSIS] Found {len(data_elements)} elements with data attributes:")
    for i, elem in enumerate(data_elements[:10]):
        print(f"  {i+1}. <{elem['tag']} {elem['data_attrs']}>{elem['text'][:30]}...")
    
    # Save a focused sample of the most relevant content
    relevant_content = []
    
    # Get calendar-related elements with more context
    for elem_info in calendar_elements[:5]:
        # Find the actual element and get more context
        relevant_content.append(f"=== CALENDAR ELEMENT ===\n{elem_info}\n")
    
    # Save relevant content
    with open('clubos_calendar_analysis.txt', 'w', encoding='utf-8') as f:
        f.write("=== CLUBOS CALENDAR ANALYSIS ===\n\n")
        f.write(f"Total HTML length: {len(html_content)} characters\n")
        f.write(f"Calendar elements found: {len(calendar_elements)}\n")
        f.write(f"Time patterns found: {len(time_patterns)}\n")
        f.write(f"Unique time patterns: {len(unique_times)}\n\n")
        
        f.write("=== CALENDAR ELEMENTS ===\n")
        for elem in calendar_elements:
            f.write(f"{elem}\n")
        
        f.write("\n=== TIME PATTERNS ===\n")
        for time_pattern in unique_times:
            f.write(f"{time_pattern}\n")
        
        f.write("\n=== API ENDPOINTS ===\n")
        for api in unique_apis:
            f.write(f"{api}\n")
    
    print(f"\n[INFO] Analysis saved to clubos_calendar_analysis.txt")
    
    # Extract a smaller, focused HTML sample
    body = soup.find('body')
    if body:
        # Look for the main content area
        main_content = (
            body.find('main') or 
            body.find('div', class_=re.compile(r'content|main|container', re.I)) or
            body.find('div', id=re.compile(r'content|main|container', re.I)) or
            body
        )
        
        if main_content:
            sample_html = str(main_content)[:10000]  # First 10k chars
            with open('clubos_calendar_sample.html', 'w', encoding='utf-8') as f:
                f.write(sample_html)
            print(f"[INFO] Saved HTML sample to clubos_calendar_sample.html")

if __name__ == "__main__":
    analyze_calendar_html()
