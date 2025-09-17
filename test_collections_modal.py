#!/usr/bin/env python3

import requests
import json
import time

def test_collections_api():
    """Test the collections API endpoints"""
    
    # Wait a moment for the dashboard to start
    print("Waiting for dashboard to start...")
    time.sleep(5)
    
    # Test the collections endpoint
    try:
        print("Testing collections API...")
        response = requests.get("http://localhost:5000/api/collections/past-due", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Collections API working! Found {data.get('total_count', 0)} past due accounts")
                
                # Show first few accounts
                past_due_data = data.get('past_due_data', [])
                print("\nFirst 5 accounts:")
                for i, account in enumerate(past_due_data[:5]):
                    print(f"  {i+1}. {account['name']}: ${account['past_due_amount']:.2f} ({account['type']})")
                    if account.get('agreement_id'):
                        print(f"      Agreement: {account['agreement_id']} - {account['agreement_type']}")
                
                return True
            else:
                print(f"❌ API returned error: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to dashboard. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_email_generation():
    """Test email generation with sample data"""
    try:
        response = requests.get("http://localhost:5000/api/collections/past-due", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                # Take first 3 accounts for testing
                test_accounts = data.get('past_due_data', [])[:3]
                
                # Test email generation
                email_data = {
                    'selected_accounts': test_accounts
                }
                
                print("\nTesting email generation...")
                email_response = requests.post(
                    "http://localhost:5000/api/collections/send-email",
                    json=email_data,
                    timeout=10
                )
                
                if email_response.status_code == 200:
                    email_result = email_response.json()
                    if email_result.get('success'):
                        print(f"✅ Email generation working! {email_result.get('message')}")
                        return True
                    else:
                        print(f"❌ Email generation error: {email_result.get('error')}")
                        return False
                else:
                    print(f"❌ Email HTTP {email_response.status_code}: {email_response.text}")
                    return False
            else:
                print(f"❌ Cannot get data for email test: {data.get('error')}")
                return False
        else:
            print(f"❌ Cannot get data for email test: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing email generation: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Collections Management System")
    print("=" * 50)
    
    # Test API
    api_working = test_collections_api()
    
    if api_working:
        # Test email generation
        email_working = test_email_generation()
        
        if email_working:
            print("\n🎉 All tests passed! Collections system is working.")
        else:
            print("\n⚠️ API working but email generation failed.")
    else:
        print("\n❌ Collections API not working. Check dashboard startup.")
