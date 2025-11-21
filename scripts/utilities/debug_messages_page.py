#!/usr/bin/env python3
"""
Debug the messages page HTML to understand the proper form structure
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.services.api.clubos_api_client import ClubOSAPIClient, ClubOSAPIAuthentication
from config.secrets_local import get_secret
import re
from bs4 import BeautifulSoup

def debug_messages_page():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    auth_service = ClubOSAPIAuthentication()
    if not auth_service.login(username, password):
        print("❌ ClubOS authentication failed")
        return
    
    client = ClubOSAPIClient(auth_service)
    print("✅ ClubOS authentication successful!")

    # Navigate to messages page
    print("\n📄 Fetching messages page...")
    messages_url = f"{client.base_url}/action/Dashboard/messages"
    headers = client.auth.get_headers()
    
    try:
        response = client.auth.session.get(messages_url, headers=headers, timeout=30, verify=False)
        print(f"   Status: {response.status_code}")
        
        if response.ok:
            print(f"   ✅ Successfully loaded messages page")
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print(f"\n🔍 Analyzing messages page HTML...")
            
            # Look for forms
            forms = soup.find_all('form')
            print(f"   Found {len(forms)} forms on the page")
            
            for i, form in enumerate(forms):
                print(f"\n   Form {i+1}:")
                print(f"     Action: {form.get('action', 'No action')}")
                print(f"     Method: {form.get('method', 'No method')}")
                print(f"     ID: {form.get('id', 'No ID')}")
                print(f"     Class: {form.get('class', 'No class')}")
                
                # Look for input fields
                inputs = form.find_all('input')
                print(f"     Input fields ({len(inputs)}):")
                for inp in inputs:
                    print(f"       - name='{inp.get('name', 'No name')}' type='{inp.get('type', 'No type')}' value='{inp.get('value', 'No value')[:50]}...'")
                
                # Look for textarea fields
                textareas = form.find_all('textarea')
                print(f"     Textarea fields ({len(textareas)}):")
                for ta in textareas:
                    print(f"       - name='{ta.get('name', 'No name')}' id='{ta.get('id', 'No ID')}'")
                
                # Look for select fields
                selects = form.find_all('select')
                print(f"     Select fields ({len(selects)}):")
                for sel in selects:
                    print(f"       - name='{sel.get('name', 'No name')}' id='{sel.get('id', 'No ID')}'")
            
            # Look for JavaScript that might handle form submission
            scripts = soup.find_all('script')
            print(f"\n   Found {len(scripts)} script tags")
            
            for i, script in enumerate(scripts):
                script_content = script.string if script.string else ''
                if 'message' in script_content.lower() or 'send' in script_content.lower():
                    print(f"\n   Script {i+1} (contains message/send keywords):")
                    print(f"     {script_content[:500]}...")
            
            # Look for AJAX endpoints or API calls
            print(f"\n🔍 Looking for AJAX endpoints...")
            ajax_patterns = [
                r'url\s*[:=]\s*["\']([^"\']+)["\']',
                r'\.ajax\([^)]*url\s*[:=]\s*["\']([^"\']+)["\']',
                r'fetch\(["\']([^"\']+)["\']',
                r'post\(["\']([^"\']+)["\']',
            ]
            
            for pattern in ajax_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                if matches:
                    print(f"   Found AJAX endpoints: {matches}")
            
            # Look for message-related elements
            print(f"\n🔍 Looking for message-related elements...")
            message_elements = soup.find_all(text=re.compile(r'message|send|text|email', re.IGNORECASE))
            if message_elements:
                print(f"   Found {len(message_elements)} message-related text elements")
                for elem in message_elements[:10]:  # Show first 10
                    print(f"     - {elem.strip()[:100]}...")
            
            # Save the full HTML for manual inspection
            with open('debug_messages_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"\n💾 Saved full HTML to debug_messages_page.html for manual inspection")
            
        else:
            print(f"   ❌ Failed to load messages page: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    debug_messages_page() 