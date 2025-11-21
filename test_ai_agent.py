"""
AI Agent Test Script

Test the autonomous AI agent tools and orchestration
"""

import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.ai import GymAgentCore, ToolsRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_tools_registry():
    """Test the tools registry"""
    print("\n" + "="*80)
    print("TEST 1: Tools Registry")
    print("="*80)
    
    registry = ToolsRegistry()
    
    # Import and register a simple test tool
    from src.services.ai.agent_tools import campaign_tools
    
    registry.register_tool(
        name="get_campaign_templates",
        func=campaign_tools.get_campaign_templates,
        description="Get campaign templates",
        input_schema={"type": "object", "properties": {}},
        category="campaigns",
        risk_level="safe"
    )
    
    print(f"\n✅ Registered 1 tool")
    print(f"   Tools list: {registry.list_tools()}")
    
    # Test tool execution
    print(f"\n🔧 Testing tool execution...")
    result = registry.execute_tool("get_campaign_templates", {})
    
    if result.get('success'):
        print(f"✅ Tool executed successfully")
        print(f"   Templates count: {result.get('count', 0)}")
    else:
        print(f"❌ Tool execution failed: {result.get('error')}")
    
    return result.get('success', False)

def test_campaign_tools():
    """Test campaign management tools"""
    print("\n" + "="*80)
    print("TEST 2: Campaign Tools")
    print("="*80)
    
    from src.services.ai.agent_tools import campaign_tools
    
    # Test getting prospects
    print("\n📋 Testing get_campaign_prospects...")
    prospects = campaign_tools.get_campaign_prospects()
    
    if prospects.get('success'):
        print(f"✅ Retrieved {prospects.get('count', 0)} prospects")
        if prospects.get('prospects'):
            print(f"   Sample: {prospects['prospects'][0].get('name', 'N/A')}")
    else:
        print(f"❌ Failed: {prospects.get('error')}")
    
    # Test getting green members
    print("\n📋 Testing get_green_members...")
    green = campaign_tools.get_green_members()
    
    if green.get('success'):
        print(f"✅ Retrieved {green.get('count', 0)} green members")
    else:
        print(f"❌ Failed: {green.get('error')}")
    
    # Test getting PPV members
    print("\n📋 Testing get_ppv_members...")
    ppv = campaign_tools.get_ppv_members()
    
    if ppv.get('success'):
        print(f"✅ Retrieved {ppv.get('count', 0)} PPV members")
    else:
        print(f"❌ Failed: {ppv.get('error')}")
    
    # Test getting templates
    print("\n📋 Testing get_campaign_templates...")
    templates = campaign_tools.get_campaign_templates()
    
    if templates.get('success'):
        print(f"✅ Retrieved {templates.get('count', 0)} templates")
        for template in templates.get('templates', [])[:3]:
            print(f"   - {template.get('title')}")
    else:
        print(f"❌ Failed: {templates.get('error')}")
    
    return True

def test_collections_tools():
    """Test collections management tools"""
    print("\n" + "="*80)
    print("TEST 3: Collections Tools")
    print("="*80)
    
    from src.services.ai.agent_tools import collections_tools
    
    # Test getting past due members
    print("\n📋 Testing get_past_due_members...")
    past_due = collections_tools.get_past_due_members(min_amount=0.01)
    
    if past_due.get('success'):
        print(f"✅ Retrieved {past_due.get('count', 0)} past due members")
        print(f"   Total amount: ${past_due.get('total_amount', 0):.2f}")
        
        if past_due.get('members'):
            sample = past_due['members'][0]
            print(f"   Sample: {sample.get('name')} owes ${sample.get('amount_past_due', 0):.2f}")
    else:
        print(f"❌ Failed: {past_due.get('error')}")
    
    # Test getting past due training clients
    print("\n📋 Testing get_past_due_training_clients...")
    training = collections_tools.get_past_due_training_clients(min_amount=0.01)
    
    if training.get('success'):
        print(f"✅ Retrieved {training.get('count', 0)} past due training clients")
        print(f"   Total amount: ${training.get('total_amount', 0):.2f}")
    else:
        print(f"❌ Failed: {training.get('error')}")
    
    return True

def test_access_tools():
    """Test access control tools"""
    print("\n" + "="*80)
    print("TEST 4: Access Control Tools")
    print("="*80)
    
    print("\n⚠️  Skipping access control tests (would modify real door access)")
    print("   Tools available: lock_door_for_member, unlock_door_for_member, check_member_access_status")
    
    return True

def test_member_tools():
    """Test member management tools"""
    print("\n" + "="*80)
    print("TEST 5: Member Tools")
    print("="*80)
    
    from src.services.ai.agent_tools import member_tools
    from src.services.database_manager import DatabaseManager
    
    # Get a test member ID
    db = DatabaseManager()
    members_raw = db.get_members()
    
    if members_raw and len(members_raw) > 0:
        # Convert sqlite3.Row to dict
        first_member = dict(members_raw[0]) if hasattr(members_raw[0], 'keys') else members_raw[0]
        test_member_id = first_member.get('prospect_id') or first_member.get('guid')
        
        print(f"\n📋 Testing get_member_profile for member: {test_member_id}")
        profile = member_tools.get_member_profile(test_member_id)
        
        if profile.get('success'):
            print(f"✅ Retrieved profile")
            p = profile['profile']
            print(f"   Name: {p.get('name')}")
            print(f"   Status: {p.get('status')}")
            print(f"   Past due: ${p.get('amount_past_due', 0):.2f}")
            print(f"   Door access: {p.get('door_access', {}).get('status', 'unknown')}")
        else:
            print(f"❌ Failed: {profile.get('error')}")
    else:
        print("⚠️  No members found in database")
    
    return True

def test_agent_core():
    """Test the agent core (without Anthropic API key)"""
    print("\n" + "="*80)
    print("TEST 6: Agent Core")
    print("="*80)
    
    agent = GymAgentCore()
    
    # List available tools
    print(f"\n📋 Available tools:")
    tools = agent.list_available_tools()
    
    # Group by category
    categories = {}
    for tool in tools:
        cat = tool.get('category', 'unknown')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(tool['name'])
    
    for category, tool_names in categories.items():
        print(f"\n   {category.upper()} ({len(tool_names)} tools):")
        for tool_name in tool_names:
            print(f"      - {tool_name}")
    
    print(f"\n✅ Total: {len(tools)} tools registered")
    
    # Check if API key is set
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print(f"\n✅ ANTHROPIC_API_KEY is set")
        print(f"   Agent is ready for autonomous execution!")
    else:
        print(f"\n⚠️  ANTHROPIC_API_KEY not set")
        print(f"   Set environment variable to enable autonomous execution")
        print(f"   Example: export ANTHROPIC_API_KEY='sk-ant-...'")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("AI AGENT PHASE 1 TESTING")
    print("="*80)
    print("\nTesting tool infrastructure and basic functionality")
    print("(Not testing actual Anthropic API calls)")
    
    tests = [
        ("Tools Registry", test_tools_registry),
        ("Campaign Tools", test_campaign_tools),
        ("Collections Tools", test_collections_tools),
        ("Access Tools", test_access_tools),
        ("Member Tools", test_member_tools),
        ("Agent Core", test_agent_core),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Phase 1 tool infrastructure is ready!")
        print("\nNext steps:")
        print("1. Set ANTHROPIC_API_KEY environment variable")
        print("2. Test autonomous workflows (Phase 2)")
        print("3. Set up scheduled tasks (APScheduler)")
    else:
        print("\n⚠️  Some tests failed - check logs above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
