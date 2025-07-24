#!/usr/bin/env python3
"""
Debug the login form to see what fields are required
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://anytime.club-os.com"
LOGIN_URL = f"{BASE_URL}/action/Login"

def debug_login_form():
    """Debug the login form structure"""
    
    print("🔍 DEBUGGING LOGIN FORM")
    print("=" * 30)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    
    try:
        # Get login page
        response = session.get(LOGIN_URL)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save the login page for inspection
        with open('login_page_debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"📄 Login page saved to login_page_debug.html")
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Final URL: {response.url}")
        
        # Find the login form
        form = soup.find('form')
        if form:
            print(f"✅ Found login form")
            print(f"   Action: {form.get('action', 'No action')}")
            print(f"   Method: {form.get('method', 'No method')}")
            
            # Find all input fields
            inputs = form.find_all('input')
            print(f"   📝 Input fields found: {len(inputs)}")
            
            for i, input_field in enumerate(inputs):
                input_type = input_field.get('type', 'text')
                input_name = input_field.get('name', 'No name')
                input_id = input_field.get('id', 'No id')
                input_value = input_field.get('value', 'No value')
                
                print(f"      {i+1}. Type: {input_type}, Name: {input_name}, ID: {input_id}, Value: {input_value}")
        
        else:
            print("❌ No login form found")
        
        # Look for any hidden fields or CSRF tokens
        hidden_inputs = soup.find_all('input', {'type': 'hidden'})
        if hidden_inputs:
            print(f"🔒 Hidden fields found: {len(hidden_inputs)}")
            for hidden in hidden_inputs:
                name = hidden.get('name', 'No name')
                value = hidden.get('value', 'No value')
                print(f"   {name}: {value}")
        
        # Look for submit buttons
        submit_buttons = soup.find_all('input', {'type': 'submit'})
        if submit_buttons:
            print(f"🚀 Submit buttons found: {len(submit_buttons)}")
            for button in submit_buttons:
                name = button.get('name', 'No name')
                value = button.get('value', 'No value')
                print(f"   {name}: {value}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_login_form() 