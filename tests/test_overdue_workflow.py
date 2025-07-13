#!/usr/bin/env python3
"""
Test script for the overdue payments workflow
Tests the complete flow without actually sending messages
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gym_bot.services.data.member_data import get_yellow_red_members, get_member_agreement_details, batch_update_past_due_amounts

def test_overdue_workflow():
    """Test the overdue payments workflow with real data"""
    print("🧪 TESTING OVERDUE PAYMENTS WORKFLOW...")
    print("=" * 60)
    
    try:
        # Step 1: Get yellow/red members
        print("📋 Step 1: Getting yellow/red members...")
        past_due_members = get_yellow_red_members()
        
        if not past_due_members:
            print("   ⚠️  No past due members found")
            return
        
        print(f"   ✅ Found {len(past_due_members)} past due members")
        
        # Step 2: Test API calls for first few members
        print("\n🔍 Step 2: Testing API calls...")
        test_count = min(5, len(past_due_members))  # Test first 5 members
        
        successful_api_calls = 0
        api_amounts_found = 0
        past_due_updates = []
        
        for i, member in enumerate(past_due_members[:test_count]):
            member_name = member['name']
            member_id = member.get('member_id', '')
            category = member.get('category', 'unknown')
            
            print(f"\n   Testing member {i+1}/{test_count}: {member_name} ({category})")
            print(f"   Member ID: {member_id}")
            
            if not member_id:
                print(f"   ❌ No member ID - skipping")
                continue
                
            # Test the agreement API call
            agreement_details = get_member_agreement_details(member_id, member_name)
            
            if agreement_details:
                successful_api_calls += 1
                amount = agreement_details.get('amount_past_due', 0)
                past_due_updates.append((member_name, amount))
                
                if amount > 0:
                    api_amounts_found += 1
                    print(f"   ✅ API SUCCESS: ${amount:.2f} past due")
                else:
                    print(f"   ℹ️  API SUCCESS: $0.00 (no amount due)")
            else:
                print(f"   ❌ API FAILED")
                past_due_updates.append((member_name, 0.0))
        
        # Step 3: Test batch update
        print(f"\n💾 Step 3: Testing batch update of {len(past_due_updates)} amounts...")
        if past_due_updates:
            update_results = batch_update_past_due_amounts(past_due_updates)
            print(f"   ✅ Updated {update_results['success_count']} members")
            if update_results['failed_count'] > 0:
                print(f"   ⚠️  Failed to update {update_results['failed_count']} members")
        
        # Summary
        print(f"\n📊 TEST SUMMARY:")
        print(f"   📋 Total past due members: {len(past_due_members)}")
        print(f"   🔍 API calls tested: {test_count}")
        print(f"   ✅ Successful API calls: {successful_api_calls}")
        print(f"   💰 Members with past due amounts: {api_amounts_found}")
        print(f"   💾 Contact list updates: {update_results.get('success_count', 0) if past_due_updates else 0}")
        
        if api_amounts_found > 0:
            print(f"\n🎉 SUCCESS! Found {api_amounts_found} members with real past due amounts")
            print(f"   The workflow is ready to send invoices for these members")
        else:
            print(f"\n⚠️  No members found with past due amounts from the API")
            print(f"   This could mean all tested members are current on payments")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_overdue_workflow()
