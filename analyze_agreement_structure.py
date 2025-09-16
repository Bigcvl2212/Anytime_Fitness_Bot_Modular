#!/usr/bin/env python3
"""
Detailed analysis of ClubOS agreement HTML structure
"""

import requests
import logging
from bs4 import BeautifulSoup
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def analyze_agreement_html():
    """Analyze the actual HTML structure of ClubOS agreements"""
    
    print("🔬 Detailed ClubOS Agreement HTML Analysis")
    print("=" * 50)
    
    # Authenticate and get agreement page
    session = requests.Session()
    
    try:
        from config.clubhub_credentials import CLUBOS_USERNAME, CLUBOS_PASSWORD
        username = CLUBOS_USERNAME
        password = CLUBOS_PASSWORD
    except ImportError:
        print("❌ Could not import ClubOS credentials")
        return
    
    # Login
    login_url = "https://anytime.club-os.com/action/Login"
    login_data = {'username': username, 'password': password}
    login_response = session.post(login_url, data=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed")
        return
    
    # Get agreement page for Dennis Rost
    test_member_id = "189425730"
    agreement_url = f"https://anytime.club-os.com/action/Agreements?memberId={test_member_id}"
    response = session.get(agreement_url)
    
    if response.status_code != 200:
        print(f"❌ Failed to get agreements")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print("🔍 ANALYZING HTML STRUCTURE")
    print("-" * 30)
    
    # Look for any elements containing "package" or "agreement"
    print("\n📦 SEARCHING FOR PACKAGE/AGREEMENT CONTENT:")
    
    # Check all text content for relevant terms
    full_text = response.text.lower()
    
    # Extract lines containing key terms
    lines = response.text.split('\n')
    relevant_lines = []
    
    keywords = ['package', 'agreement', 'session', 'training', 'purchased', 'used', 'remaining', 'expire']
    
    for line_num, line in enumerate(lines, 1):
        line_lower = line.lower()
        for keyword in keywords:
            if keyword in line_lower and line.strip():
                relevant_lines.append((line_num, keyword, line.strip()))
                break
    
    print(f"Found {len(relevant_lines)} relevant lines:")
    for line_num, keyword, line in relevant_lines[:20]:  # Show first 20
        print(f"  Line {line_num} ({keyword}): {line[:100]}{'...' if len(line) > 100 else ''}")
    
    if len(relevant_lines) > 20:
        print(f"  ... and {len(relevant_lines) - 20} more lines")
    
    # Look for specific HTML patterns
    print("\n🏗️ HTML STRUCTURE ANALYSIS:")
    
    # Look for any tables
    tables = soup.find_all('table')
    print(f"📊 Tables found: {len(tables)}")
    
    for i, table in enumerate(tables):
        print(f"  Table {i+1}: {len(table.find_all('tr'))} rows")
        rows = table.find_all('tr')
        if rows:
            first_row_text = rows[0].get_text(strip=True)
            print(f"    First row: {first_row_text[:50]}...")
    
    # Look for divs with class attributes
    divs_with_class = soup.find_all('div', class_=True)
    print(f"\n📋 Divs with classes: {len(divs_with_class)}")
    
    class_names = set()
    for div in divs_with_class:
        classes = div.get('class', [])
        for cls in classes:
            class_names.add(cls)
    
    print(f"  Unique classes: {sorted(class_names)}")
    
    # Look for any elements containing specific patterns
    print("\n🔍 PATTERN MATCHING:")
    
    # Pattern for session counts (e.g., "12 of 20", "5/10", "Remaining: 8")
    session_patterns = [
        r'\b\d+\s*of\s*\d+\b',
        r'\b\d+/\d+\b',
        r'remaining[:]\s*\d+',
        r'used[:]\s*\d+',
        r'sessions[:]\s*\d+'
    ]
    
    for pattern in session_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            print(f"  Pattern '{pattern}': {matches[:5]}")  # Show first 5 matches
    
    # Look for JavaScript that might contain data
    scripts = soup.find_all('script')
    print(f"\n💻 JavaScript sections: {len(scripts)}")
    
    for i, script in enumerate(scripts):
        script_text = script.get_text()
        if script_text and any(keyword in script_text.lower() for keyword in keywords):
            print(f"  Script {i+1} contains relevant keywords ({len(script_text)} chars)")
            # Show a sample
            for line in script_text.split('\n')[:5]:
                if any(keyword in line.lower() for keyword in keywords):
                    print(f"    {line.strip()[:80]}...")
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    analyze_agreement_html()
