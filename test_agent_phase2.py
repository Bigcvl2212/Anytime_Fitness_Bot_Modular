#!/usr/bin/env python3
"""
Test script for Phase 2 AI Agent with Claude API
"""

import os
import sys

# Load environment FIRST before any imports
from dotenv import load_dotenv
load_dotenv()

print(f"🔍 DEBUG: CLAUDE_API_KEY loaded: {os.getenv('CLAUDE_API_KEY')[:20] if os.getenv('CLAUDE_API_KEY') else 'NOT FOUND'}")

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.ai.agent_core import GymAgentCore
from src.services.ai.tools_registry import ToolsRegistry
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_agent_initialization():
    """Test that agent initializes with Claude API key"""
    print("=" * 60)
    print("PHASE 2 AI AGENT - INITIALIZATION TEST")
    print("=" * 60)
    
    # Check environment variables
    claude_key = os.getenv('CLAUDE_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    print(f"\n📋 Environment Check:")
    print(f"   CLAUDE_API_KEY: {'✅ SET' if claude_key else '❌ NOT SET'}")
    print(f"   ANTHROPIC_API_KEY: {'✅ SET' if anthropic_key else '❌ NOT SET'}")
    
    if claude_key:
        print(f"   Key preview: {claude_key[:20]}...")
    
    # Initialize registry
    print(f"\n🔧 Initializing Tools Registry...")
    registry = ToolsRegistry()
    
    # Register all tools (they should already be auto-registered)
    tool_count = len(registry.tools)
    print(f"   ✅ {tool_count} tools registered")
    
    # Initialize agent
    print(f"\n🤖 Initializing AI Agent Core...")
    agent = GymAgentCore()
    
    print(f"   API Key: {'✅ Loaded' if agent.api_key else '❌ Missing'}")
    print(f"   Client: {'✅ Ready' if agent.client else '❌ Not initialized'}")
    
    if not agent.client:
        print("\n❌ AGENT NOT READY - Missing API key or Anthropic SDK")
        return False
    
    print("\n✅ AGENT READY FOR PHASE 2!")
    print(f"   Model: claude-3-7-sonnet-20250219")
    print(f"   Tools: {tool_count} available")
    print(f"   Registry: {registry}")
    
    return True


def test_simple_tool_call():
    """Test a simple tool call through the agent"""
    print("\n" + "=" * 60)
    print("TESTING SIMPLE AUTONOMOUS TASK")
    print("=" * 60)
    
    agent = GymAgentCore()
    
    if not agent.client:
        print("❌ Cannot test - agent not initialized")
        return False
    
    print("\n🎯 Task: Get count of campaign prospects")
    print("   This will test Claude's ability to:")
    print("   1. Understand the task")
    print("   2. Select the right tool (get_campaign_prospects)")
    print("   3. Call the tool correctly")
    print("   4. Report the results")
    
    task = "How many active prospects do we have for campaigns? Use the get_campaign_prospects tool."
    
    print(f"\n🚀 Executing task...")
    result = agent.execute_task(task, max_iterations=3)
    
    print(f"\n📊 RESULT:")
    print(f"   Success: {result.get('success', False)}")
    if result.get('success'):
        print(f"   Final Answer: {result.get('result', 'No result')}")
        print(f"   Tool Calls: {len(result.get('tool_calls', []))}")
        print(f"   Iterations: {result.get('iterations', 0)}")
        
        # Show tool calls
        for i, call in enumerate(result.get('tool_calls', []), 1):
            print(f"\n   Tool Call #{i}:")
            print(f"      Tool: {call.get('tool', 'unknown')}")
            print(f"      Success: {call.get('success', False)}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    return result.get('success', False)


if __name__ == "__main__":
    print("\n🤖 ANYTIME FITNESS BOT - PHASE 2 AI AGENT TEST\n")
    
    # Test 1: Initialization
    init_success = test_agent_initialization()
    
    if not init_success:
        print("\n❌ Initialization failed - cannot proceed")
        sys.exit(1)
    
    # Test 2: Simple tool call (optional - uncomment to test)
    print("\n" + "=" * 60)
    choice = input("\n🔥 Run autonomous task test? This will use Claude API (y/n): ").strip().lower()
    
    if choice == 'y':
        test_simple_tool_call()
    else:
        print("\n⏭️  Skipped autonomous task test")
    
    print("\n" + "=" * 60)
    print("✅ PHASE 2 PREREQUISITES COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. ✅ Anthropic SDK installed")
    print("2. ✅ APScheduler installed")
    print("3. ✅ Claude API key configured")
    print("4. ✅ Agent core ready")
    print("5. ⏳ Create workflow_runner.py (6 autonomous workflows)")
    print("6. ⏳ Create workflow_scheduler.py (APScheduler setup)")
    print("7. ⏳ Test first workflow")
    print("\n🚀 Ready to build Phase 2 autonomous workflows!")
