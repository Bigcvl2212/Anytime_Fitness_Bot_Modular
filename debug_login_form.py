"""
Debug Login Form Analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from bs4 import BeautifulSoup

def analyze_login_form():
    """Analyze the login form in detail"""
    print("🔍 Analyzing login form in detail...")
    
    # Get the login page
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    
    login_url = "https://anytime.club-os.com/action/Login/view?__fsk=1221801756"
    response = session.get(login_url)
    
    print(f"📊 Status: {response.status_code}")
    print(f"🔗 URL: {response.url}")
    
    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find ALL forms on the page
    forms = soup.find_all('form')
    print(f"📝 Found {len(forms)} forms on the page")
    
    for i, form in enumerate(forms):
        print(f"\n🔍 Form {i+1}:")
        print(f"   Action: {form.get('action', 'No action')}")
        print(f"   Method: {form.get('method', 'GET')}")
        print(f"   ID: {form.get('id', 'No ID')}")
        print(f"   Class: {form.get('class', 'No class')}")
        
        # Find all inputs in this form
        inputs = form.find_all('input')
        print(f"   📋 Inputs ({len(inputs)}):")
        
        for input_field in inputs:
            name = input_field.get('name', 'No name')
            input_type = input_field.get('type', 'text')
            value = input_field.get('value', '')
            required = input_field.get('required', False)
            placeholder = input_field.get('placeholder', '')
            
            print(f"      - {name}: type={input_type}, value='{value[:30]}...', required={required}, placeholder='{placeholder}'")
        
        # Find buttons
        buttons = form.find_all(['button', 'input'], {'type': ['submit', 'button']})
        print(f"   🔘 Buttons ({len(buttons)}):")
        for button in buttons:
            button_type = button.get('type', 'button')
            button_value = button.get('value', button.text if hasattr(button, 'text') else '')
            button_class = button.get('class', [])
            print(f"      - Type: {button_type}, Value: '{button_value}', Class: {button_class}")
    
    # Also check for any JavaScript that might be modifying the form
    scripts = soup.find_all('script')
    form_related_scripts = []
    
    for script in scripts:
        if script.string:
            script_text = script.string.lower()
            if any(keyword in script_text for keyword in ['form', 'login', 'submit', 'username', 'password']):
                form_related_scripts.append(script.string[:500] + "..." if len(script.string) > 500 else script.string)
    
    print(f"\n🔧 Found {len(form_related_scripts)} scripts with form-related keywords")
    for i, script in enumerate(form_related_scripts[:3]):  # Show first 3
        print(f"Script {i+1}: {script[:200]}...")
    
    # Save the full login page for manual inspection
    with open("data/debug_outputs/login_page_analysis.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"\n💾 Saved full login page to data/debug_outputs/login_page_analysis.html")

if __name__ == "__main__":
    analyze_login_form()
