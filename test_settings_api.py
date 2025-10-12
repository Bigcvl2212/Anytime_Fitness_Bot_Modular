"""
Test Settings API
Verify that the settings system backend is working correctly
"""

import requests
import json
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:5000"

def test_settings_api():
    """Test all settings API endpoints"""
    
    print("Testing Settings API")
    print("=" * 60)
    
    # Test 1: Get all settings
    print("\n1️⃣ GET /api/settings - Get all settings")
    response = requests.get(f"{BASE_URL}/api/settings")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success! Found {len(data.get('settings', {}))} categories")
        for category in data.get('settings', {}).keys():
            print(f"      - {category}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test 2: Get AI Agent settings
    print("\n2️⃣ GET /api/settings/ai_agent - Get AI Agent category")
    response = requests.get(f"{BASE_URL}/api/settings/ai_agent")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        settings = data.get('settings', {})
        print(f"   ✅ Success! Found {len(settings)} settings in ai_agent")
        for key, value in settings.items():
            print(f"      - {key}: {value}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test 3: Get specific setting
    print("\n3️⃣ GET /api/settings/ai_agent/max_iterations - Get specific setting")
    response = requests.get(f"{BASE_URL}/api/settings/ai_agent/max_iterations")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success! max_iterations = {data.get('value')}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test 4: Update a setting
    print("\n4️⃣ PUT /api/settings/ai_agent/max_iterations - Update setting")
    payload = {
        "value": 15,
        "user": "test_script",
        "reason": "Testing settings API"
    }
    response = requests.put(
        f"{BASE_URL}/api/settings/ai_agent/max_iterations",
        json=payload
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success! Updated to {data.get('value')}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test 5: Verify update
    print("\n5️⃣ GET /api/settings/ai_agent/max_iterations - Verify update")
    response = requests.get(f"{BASE_URL}/api/settings/ai_agent/max_iterations")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        value = data.get('value')
        print(f"   ✅ Success! Value is now {value}")
        if value == 15:
            print(f"   ✅ Update verified!")
        else:
            print(f"   ⚠️ Unexpected value: {value}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test 6: Get setting history
    print("\n6️⃣ GET /api/settings/history/ai_agent/max_iterations - Get history")
    response = requests.get(f"{BASE_URL}/api/settings/history/ai_agent/max_iterations")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        history = data.get('history', [])
        print(f"   ✅ Success! Found {len(history)} history entries")
        for entry in history[:3]:  # Show first 3
            print(f"      - {entry.get('changed_at')}: {entry.get('old_value')} → {entry.get('new_value')} by {entry.get('changed_by')}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test 7: Bulk update category
    print("\n7️⃣ PUT /api/settings/ai_agent - Bulk update category")
    payload = {
        "settings": {
            "max_iterations": 10,
            "confidence_threshold": "high",
            "dry_run_mode": False
        },
        "user": "test_script",
        "reason": "Testing bulk update"
    }
    response = requests.put(
        f"{BASE_URL}/api/settings/ai_agent",
        json=payload
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success! Updated {data.get('updated')}/{len(payload['settings'])} settings")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test 8: Get defaults
    print("\n8️⃣ GET /api/settings/defaults - Get all defaults")
    response = requests.get(f"{BASE_URL}/api/settings/defaults")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        defaults = data.get('defaults', {})
        print(f"   ✅ Success! Found defaults for {len(defaults)} categories")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test 9: Reset category to defaults
    print("\n9️⃣ POST /api/settings/reset/ai_agent - Reset to defaults")
    response = requests.post(
        f"{BASE_URL}/api/settings/reset/ai_agent",
        json={"user": "test_script"}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success! {data.get('message')}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test 10: Export settings
    print("\n🔟 GET /api/settings/export - Export all settings")
    response = requests.get(f"{BASE_URL}/api/settings/export")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        settings_json = data.get('settings_json', '{}')
        settings_data = json.loads(settings_json)
        print(f"   ✅ Success! Exported {len(settings_data)} categories")
        print(f"   📄 Sample: {list(settings_data.keys())[:3]}...")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    print("\n" + "=" * 60)
    print("✅ Settings API test complete!")
    print("\nNext steps:")
    print("1. Review the test results above")
    print("2. Check that settings are persisted in gym_bot.db")
    print("3. Build the frontend settings page")


if __name__ == "__main__":
    try:
        test_settings_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to Flask server")
        print("   Make sure the dashboard is running at http://localhost:5000")
        print("   Run: python run_dashboard.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
