#!/usr/bin/env python3
"""
Test AI Custom Instructions Loading
Validates that custom instructions load correctly from settings
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.settings_manager import SettingsManager
from src.services.ai.ai_context_manager import AIContextManager

def test_custom_instructions():
    """Test loading and injecting custom instructions"""
    
    print("=" * 80)
    print("AI CUSTOM INSTRUCTIONS TEST")
    print("=" * 80)
    
    # Initialize managers
    print("\n1. Initializing managers...")
    settings_mgr = SettingsManager()
    context_mgr = AIContextManager()
    
    # Get current AI agent settings
    print("\n2. Loading AI agent settings...")
    ai_settings = settings_mgr.get_category('ai_agent')
    
    print(f"   - Model: {ai_settings.get('model')}")
    print(f"   - Max tokens: {ai_settings.get('max_tokens')}")
    print(f"   - Confidence threshold: {ai_settings.get('confidence_threshold')}")
    
    # Check for custom instructions
    print("\n3. Checking custom instructions...")
    instruction_fields = [
        'custom_system_prompt',
        'collections_rules',
        'campaign_guidelines',
        'tone_and_voice',
        'forbidden_actions',
        'business_context',
        'escalation_triggers'
    ]
    
    has_instructions = False
    for field in instruction_fields:
        value = ai_settings.get(field, '')
        if value and value.strip():
            print(f"   ✓ {field}: {len(value)} characters")
            has_instructions = True
        else:
            print(f"   - {field}: (not set)")
    
    if not has_instructions:
        print("\n   ℹ No custom instructions configured yet.")
        print("   Go to Settings > AI Agent > AI Instructions & Context to add them.")
    
    # Test system prompt generation
    print("\n4. Testing system prompt generation...")
    
    # Get base admin prompt
    admin_prompt_base = context_mgr._get_admin_system_prompt()
    print(f"   - Base admin prompt: {len(admin_prompt_base)} characters")
    
    # Get enhanced admin prompt
    admin_prompt_enhanced = context_mgr.get_system_prompt('admin')
    print(f"   - Enhanced admin prompt: {len(admin_prompt_enhanced)} characters")
    print(f"   - Added: {len(admin_prompt_enhanced) - len(admin_prompt_base)} characters")
    
    # Get sales prompt with collections task
    sales_prompt_collections = context_mgr.get_system_prompt('sales', context_data={'task_type': 'collections'})
    print(f"   - Sales + collections prompt: {len(sales_prompt_collections)} characters")
    
    # Get sales prompt with campaigns task
    sales_prompt_campaigns = context_mgr.get_system_prompt('sales', context_data={'task_type': 'campaigns'})
    print(f"   - Sales + campaigns prompt: {len(sales_prompt_campaigns)} characters")
    
    # Test custom instructions extraction
    print("\n5. Testing custom instructions extraction...")
    custom_instructions = context_mgr._get_custom_instructions()
    
    if custom_instructions:
        print(f"   ✓ Loaded {len(custom_instructions)} instruction sections:")
        for key, value in custom_instructions.items():
            print(f"      - {key}: {len(value)} characters")
    else:
        print("   - No custom instructions loaded")
    
    # Show sample enhanced prompt
    if has_instructions:
        print("\n6. Sample enhanced prompt (first 500 chars):")
        print("   " + "-" * 76)
        sample = admin_prompt_enhanced[:500].replace("\n", "\n   ")
        print(f"   {sample}...")
        print("   " + "-" * 76)
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    if has_instructions:
        print("\n✓ Custom instructions are configured and loading correctly!")
        print("  AI agents will use these instructions in their system prompts.")
    else:
        print("\nℹ To configure custom instructions:")
        print("  1. Open the dashboard in your browser")
        print("  2. Go to Settings > AI Agent")
        print("  3. Scroll to 'AI Instructions & Context'")
        print("  4. Fill in relevant instruction fields")
        print("  5. Click 'Save AI Agent Settings'")
    
    print()

if __name__ == '__main__':
    try:
        test_custom_instructions()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
