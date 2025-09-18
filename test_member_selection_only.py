#!/usr/bin/env python3
"""
Test Messaging Route Query Only
Just test the member selection part WITHOUT sending any messages
"""

import requests
import json

def test_member_selection_only():
    """Test just the member selection part of the campaign route"""
    
    print("🔍 TESTING MEMBER SELECTION (NO MESSAGES SENT)")
    print("=" * 60)
    
    # Test the member categories endpoint first
    print("\n1. TESTING MEMBER CATEGORIES ENDPOINT")
    print("-" * 40)
    
    try:
        response = requests.get('http://localhost:5000/api/members/categories', timeout=10)
        print(f"Categories endpoint status: {response.status_code}")
        if response.status_code == 200:
            categories = response.json()
            print(f"Available categories: {len(categories.get('categories', []))}")
            
            # Look for past due categories
            for cat in categories.get('categories', []):
                if 'past due' in cat.get('name', '').lower():
                    print(f"  - {cat.get('name')}: {cat.get('count')} members")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing categories: {e}")
    
    # Test direct member query
    print("\n2. TESTING DIRECT MEMBER QUERY")
    print("-" * 40)
    
    try:
        response = requests.get('http://localhost:5000/api/members/past-due', timeout=10)
        print(f"Past due members endpoint status: {response.status_code}")
        if response.status_code == 200:
            past_due = response.json()
            members = past_due.get('members', [])
            print(f"Past due members found: {len(members)}")
            
            if members:
                print("Sample member data:")
                sample = members[0]
                print(f"  Name: {sample.get('full_name')}")
                print(f"  Email: {sample.get('email')}")
                print(f"  Phone: {sample.get('mobile_phone')}")
                print(f"  Status: {sample.get('status_message')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing past due members: {e}")

if __name__ == "__main__":
    test_member_selection_only()