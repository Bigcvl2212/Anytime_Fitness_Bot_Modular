#!/usr/bin/env python3
"""Quick debug script for ClubOS login analysis"""
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('CLUBOS_USERNAME', 'j.mayo')
password = os.getenv('CLUBOS_PASSWORD')

print(f'Using credentials: {username} / {password[:3]}***{password[-3:]}')

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

# Get login page
login_url = 'https://anytime.club-os.com/action/Login/view?__fsk=1221801756'
resp = session.get(login_url)
print(f'Login page status: {resp.status_code}')

# Parse form
soup = BeautifulSoup(resp.text, 'html.parser')
forms = soup.find_all('form')
print(f'Found {len(forms)} forms')

for i, form in enumerate(forms):
    print(f'\nForm {i+1}:')
    print(f'  Action: {form.get("action")}')
    print(f'  Method: {form.get("method")}')
    
    inputs = form.find_all('input')
    for inp in inputs:
        name = inp.get('name', 'unnamed')
        value = inp.get('value', '')
        inp_type = inp.get('type', 'text')
        if value:
            print(f'  [{inp_type}] {name} = {value[:40]}...')
        else:
            print(f'  [{inp_type}] {name} = (empty)')

# Try to submit login
print('\n\n--- Attempting Login ---')
form_data = {}
first_form = forms[0] if forms else None
if first_form:
    for inp in first_form.find_all('input'):
        name = inp.get('name')
        if name:
            form_data[name] = inp.get('value', '')
    
    form_data['username'] = username
    form_data['password'] = password
    
    print(f'Submitting with fields: {list(form_data.keys())}')
    
    login_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://anytime.club-os.com',
        'Referer': login_url,
    }
    
    login_resp = session.post(login_url, data=form_data, headers=login_headers, allow_redirects=True)
    print(f'Login response: {login_resp.status_code}')
    print(f'Final URL: {login_resp.url}')
    print(f'Cookies: {list(session.cookies.keys())}')
    
    # Check if we stayed on login or got redirected
    if 'Login' in login_resp.url:
        print('FAILED: Still on login page')
        # Check for error messages
        soup2 = BeautifulSoup(login_resp.text, 'html.parser')
        errors = soup2.find_all(class_='error') or soup2.find_all(class_='alert')
        if errors:
            print(f'Error messages: {[e.text.strip() for e in errors]}')
    else:
        print('SUCCESS: Redirected away from login')
        print(f'loggedInUserId cookie: {session.cookies.get("loggedInUserId")}')
