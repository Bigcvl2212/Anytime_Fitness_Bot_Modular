"""
Test Phase 3A Backend APIs

Quick test script to verify workflow management and conversation APIs
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_workflow_apis():
    """Test workflow management endpoints"""
    print("\n" + "="*60)
    print("TESTING PHASE 3A BACKEND APIS")
    print("="*60)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing /api/ai/workflows/health...")
    try:
        response = requests.get(f"{BASE_URL}/api/ai/workflows/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Get Workflows Status
    print("\n2️⃣ Testing /api/ai/workflows/status...")
    try:
        response = requests.get(f"{BASE_URL}/api/ai/workflows/status")
        print(f"   Status: {response.status_code}")
        data = response.json()
        if data.get('success'):
            print(f"   ✅ Found {len(data.get('workflows', []))} workflows")
            for wf in data.get('workflows', [])[:2]:  # Show first 2
                print(f"      • {wf['name']} - Status: {wf.get('next_run', 'N/A')}")
        else:
            print(f"   Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Get Workflow Config
    print("\n3️⃣ Testing /api/ai/workflows/daily_campaigns/config...")
    try:
        response = requests.get(f"{BASE_URL}/api/ai/workflows/daily_campaigns/config")
        print(f"   Status: {response.status_code}")
        data = response.json()
        if data.get('success'):
            print(f"   ✅ Config loaded")
            config = data.get('config', {})
            print(f"      Schedule: {config.get('schedule', 'N/A')}")
            print(f"      Dry Run: {config.get('dry_run', 'N/A')}")
        else:
            print(f"   Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Get Available Tools
    print("\n4️⃣ Testing /api/ai/conversation/tools...")
    try:
        response = requests.get(f"{BASE_URL}/api/ai/conversation/tools")
        print(f"   Status: {response.status_code}")
        data = response.json()
        if data.get('success'):
            print(f"   ✅ Found {data.get('count', 0)} tools")
            for tool in data.get('tools', [])[:3]:  # Show first 3
                print(f"      • {tool.get('name', 'N/A')} ({tool.get('category', 'N/A')})")
        else:
            print(f"   Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Get Conversation History
    print("\n5️⃣ Testing /api/ai/conversation/history...")
    try:
        response = requests.get(f"{BASE_URL}/api/ai/conversation/history?limit=5")
        print(f"   Status: {response.status_code}")
        data = response.json()
        if data.get('success'):
            print(f"   ✅ Found {data.get('count', 0)} messages")
        else:
            print(f"   Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 6: Get Pending Approvals
    print("\n6️⃣ Testing /api/ai/conversation/approvals/pending...")
    try:
        response = requests.get(f"{BASE_URL}/api/ai/conversation/approvals/pending")
        print(f"   Status: {response.status_code}")
        data = response.json()
        if data.get('success'):
            print(f"   ✅ Found {data.get('count', 0)} pending approvals")
        else:
            print(f"   Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*60)
    print("✅ PHASE 3A BACKEND API TESTS COMPLETE")
    print("="*60)
    print("\n💡 Next Steps:")
    print("   1. Start dashboard: python run_dashboard.py")
    print("   2. Visit: http://localhost:5000/api/ai/workflows/status")
    print("   3. Begin Phase 3B: Build frontend dashboard")
    print()

if __name__ == "__main__":
    print("⚠️  Make sure the dashboard is running first:")
    print("   python run_dashboard.py")
    print()
    input("Press Enter when dashboard is ready...")
    
    test_workflow_apis()
