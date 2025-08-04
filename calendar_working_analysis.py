#!/usr/bin/env python3
"""
Extract calendar data from the HTML page directly using the working authentication method
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clubos_integration_fixed import ClubOSIntegration
import re
import json
import logging
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_working_calendar_data():
    """Extract calendar data using the working authentication approach"""
    
    print("=== Extracting Calendar Data from HTML (Working Method) ===")
    
    # Initialize and connect using the working method
    client = ClubOSIntegration()
    
    print("🔐 Connecting to ClubOS using working method...")
    if not client.connect():
        print("❌ Connection failed")
        return
    
    print("✅ Connected successfully!")
    
    # Get calendar page HTML using the working approach
    print("📅 Loading calendar page...")
    
    # Visit dashboard first (this is what the working method does)
    dashboard_response = client.client.session.get(f"{client.client.base_url}/action/Dashboard")
    if dashboard_response.ok:
        print(f"📊 Dashboard page loaded ({len(dashboard_response.text)} characters)")
        
        # Save dashboard for analysis
        with open("data/debug_outputs/calendar_dashboard_content.html", "w", encoding="utf-8") as f:
            f.write(dashboard_response.text)
    
    # Now get calendar page
    calendar_response = client.client.session.get(f"{client.client.base_url}/action/Calendar")
    
    if not calendar_response.ok:
        print(f"❌ Failed to load calendar page: {calendar_response.status_code}")
        print(f"Response: {calendar_response.text[:500]}")
        return
    
    html_content = calendar_response.text
    print(f"📄 Calendar page loaded ({len(html_content)} characters)")
    
    # Save the full calendar HTML for analysis
    with open("data/debug_outputs/calendar_working_content.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Parse with BeautifulSoup for better HTML analysis
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check if we're actually on a calendar page or redirected to login
    page_title = soup.find('title')
    if page_title:
        print(f"📄 Page title: {page_title.get_text()}")
    
    # Look for calendar-specific elements
    print("\n=== Analyzing Calendar Page Structure ===")
    
    # Look for calendar containers
    calendar_containers = soup.find_all(['div', 'section'], class_=re.compile(r'calendar|event|schedule', re.I))
    print(f"Found {len(calendar_containers)} potential calendar containers")
    
    # Look for JavaScript calendar data
    print("\n=== Searching for Calendar Data in JavaScript ===")
    
    script_tags = soup.find_all('script')
    calendar_data_found = False
    
    for i, script in enumerate(script_tags):
        if script.string:
            script_content = script.string
            
            # Look for calendar-related variables
            patterns = [
                r'var\s+events\s*=\s*(\[.*?\]);',
                r'events\s*:\s*(\[.*?\])',
                r'calendar.*?data\s*:\s*(\{.*?\})',
                r'calendar.*?events\s*:\s*(\[.*?\])',
                r'"events"\s*:\s*(\[.*?\])',
                r'eventData\s*=\s*(\[.*?\]);',
                r'calendarEvents\s*=\s*(\[.*?\]);',
                r'sessions\s*:\s*(\[.*?\])',
                r'appointments\s*:\s*(\[.*?\])'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, script_content, re.DOTALL | re.IGNORECASE)
                if matches:
                    print(f"📅 Found calendar data in script {i+1}:")
                    for j, match in enumerate(matches[:2]):  # Show first 2
                        try:
                            # Try to parse as JSON
                            data = json.loads(match)
                            print(f"  Match {j+1}: Valid JSON with {len(data) if isinstance(data, (list, dict)) else 'unknown'} items")
                            if isinstance(data, list) and len(data) > 0:
                                print(f"    First item: {str(data[0])[:200]}...")
                                calendar_data_found = True
                            elif isinstance(data, dict):
                                print(f"    Keys: {list(data.keys())[:10]}")
                                calendar_data_found = True
                        except:
                            print(f"  Match {j+1}: {match[:200]}...")
                            if len(match.strip()) > 10:  # If it looks like actual data
                                calendar_data_found = True
    
    # Look for AJAX endpoints and API calls
    print("\n=== Searching for AJAX Endpoints ===")
    
    ajax_endpoints = set()
    all_scripts = '\n'.join([script.string or '' for script in script_tags])
    
    ajax_patterns = [
        r'ajax\([\'"]([^\'"]+)[\'"]',
        r'\.get\([\'"]([^\'"]+)[\'"]',
        r'\.post\([\'"]([^\'"]+)[\'"]',
        r'url\s*:\s*[\'"]([^\'"]+)[\'"]',
        r'endpoint\s*:\s*[\'"]([^\'"]+)[\'"]',
        r'/api/[^\'"\s]+',
        r'/ajax/[^\'"\s]+',
        r'/action/[^\'"\s]+'
    ]
    
    for pattern in ajax_patterns:
        matches = re.findall(pattern, all_scripts, re.IGNORECASE)
        for match in matches:
            if any(keyword in match.lower() for keyword in ['calendar', 'event', 'session', 'appointment', 'schedule']):
                ajax_endpoints.add(match)
    
    if ajax_endpoints:
        print("Found potential calendar endpoints:")
        for endpoint in sorted(ajax_endpoints):
            print(f"  {endpoint}")
    
    # Look for forms that might be related to calendar operations
    print("\n=== Searching for Calendar Forms ===")
    
    forms = soup.find_all('form')
    calendar_forms = []
    
    for form in forms:
        # Check if form is calendar-related
        form_str = str(form).lower()
        if any(keyword in form_str for keyword in ['calendar', 'event', 'session', 'appointment', 'book']):
            calendar_forms.append(form)
            print(f"📝 Found calendar form: {form.get('action', 'No action')} - {form.get('method', 'GET')}")
            
            # Look for hidden inputs that might be needed
            hidden_inputs = form.find_all('input', type='hidden')
            if hidden_inputs:
                print(f"  Hidden inputs: {[(inp.get('name'), inp.get('value', '')[:20]) for inp in hidden_inputs[:5]]}")
    
    # Look for calendar-specific tables or lists
    print("\n=== Searching for Calendar Tables/Lists ===")
    
    # Look for tables that might contain calendar data
    tables = soup.find_all('table')
    calendar_tables = []
    
    for table in tables:
        table_str = str(table).lower()
        if any(keyword in table_str for keyword in ['calendar', 'event', 'session', 'time', 'date', 'appointment']):
            calendar_tables.append(table)
            print(f"📊 Found potential calendar table with {len(table.find_all('tr'))} rows")
    
    # Look for lists that might contain sessions/events
    lists = soup.find_all(['ul', 'ol'])
    calendar_lists = []
    
    for lst in lists:
        list_str = str(lst).lower()
        if any(keyword in list_str for keyword in ['event', 'session', 'class', 'appointment']):
            calendar_lists.append(lst)
            print(f"📋 Found potential calendar list with {len(lst.find_all('li'))} items")
    
    # Check for calendar-specific divs or sections
    print("\n=== Searching for Calendar Content Divs ===")
    
    calendar_divs = soup.find_all('div', {'id': re.compile(r'calendar|event|schedule', re.I)})
    calendar_divs.extend(soup.find_all('div', {'class': re.compile(r'calendar|event|schedule', re.I)}))
    
    print(f"Found {len(calendar_divs)} divs with calendar-related IDs or classes")
    
    # Summary
    print(f"\n=== Calendar Data Analysis Summary ===")
    print(f"📄 Page loaded: {len(html_content)} characters")
    print(f"📅 Calendar data in JS: {'Yes' if calendar_data_found else 'No'}")
    print(f"🔗 AJAX endpoints found: {len(ajax_endpoints)}")
    print(f"📝 Calendar forms found: {len(calendar_forms)}")
    print(f"📊 Calendar tables found: {len(calendar_tables)}")
    print(f"📋 Calendar lists found: {len(calendar_lists)}")
    print(f"🔲 Calendar divs found: {len(calendar_divs)}")
    
    # Try to test some of the found endpoints
    if ajax_endpoints:
        print(f"\n=== Testing Found Endpoints ===")
        for endpoint in list(ajax_endpoints)[:3]:  # Test first 3
            try:
                if endpoint.startswith('/'):
                    full_url = f"{client.client.base_url}{endpoint}"
                else:
                    full_url = endpoint
                
                print(f"🔄 Testing endpoint: {endpoint}")
                test_response = client.client.session.get(full_url)
                print(f"  Status: {test_response.status_code}")
                if test_response.ok and len(test_response.text) > 0:
                    print(f"  Content: {test_response.text[:100]}...")
                    
                    # Try to parse as JSON
                    try:
                        json_data = test_response.json()
                        print(f"  JSON response with {len(json_data) if isinstance(json_data, (list, dict)) else 'unknown'} items")
                    except:
                        pass
                        
            except Exception as e:
                print(f"  Error testing endpoint: {e}")
    
    print("\n✅ Working calendar analysis complete!")
    
    return {
        'calendar_data_found': calendar_data_found,
        'ajax_endpoints': list(ajax_endpoints),
        'forms_count': len(calendar_forms),
        'tables_count': len(calendar_tables),
        'html_size': len(html_content)
    }

if __name__ == "__main__":
    result = extract_working_calendar_data()
    print(f"\nFinal result: {result}")
