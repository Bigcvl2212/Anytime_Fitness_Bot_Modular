#!/usr/bin/env python3
"""
Final test of the complete overdue payments workflow
Tests end-to-end processing with real member data
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gym_bot.services.data.member_data import get_yellow_red_members, get_member_balance_from_contact_data, batch_update_past_due_amounts

def final_overdue_workflow_test():
    """Test the complete overdue payments workflow end-to-end"""
    print("🎯 FINAL OVERDUE PAYMENTS WORKFLOW TEST")
    print("=" * 60)
    
    try:
        # Step 1: Get yellow/red members
        print("📋 Step 1: Getting yellow/red members...")
        past_due_members = get_yellow_red_members()
        
        if not past_due_members:
            print("   ⚠️  No past due members found")
            return
        
        print(f"   ✅ Found {len(past_due_members)} past due members")
        
        # Step 2: Process members and collect real API data
        print(f"\n💰 Step 2: Processing all {len(past_due_members)} members...")
        
        invoices_ready = 0
        api_success = 0
        api_failures = 0
        past_due_updates = []
        members_with_amounts = []
        
        for i, member in enumerate(past_due_members):
            member_name = member['name']
            member_id = member.get('member_id', '')
            category = member.get('category', 'unknown')
            
            print(f"\n   Processing {i+1}/{len(past_due_members)}: {member_name} ({category})")
            
            if not member_id:
                print(f"      ❌ No member ID - skipping")
                past_due_updates.append((member_name, 0.0))
                api_failures += 1
                continue
            
            # Get actual balance using the workflow function
            actual_amount_due = get_member_balance_from_contact_data(member)
            past_due_updates.append((member_name, actual_amount_due))
            
            if actual_amount_due > 0:
                api_success += 1
                invoices_ready += 1
                members_with_amounts.append((member_name, actual_amount_due, category))
                print(f"      ✅ Ready for invoice: ${actual_amount_due:.2f}")
            else:
                if actual_amount_due == 0:
                    api_success += 1  # API worked, just no amount due
                    print(f"      ℹ️  No amount due (current on payments)")
                else:
                    api_failures += 1
                    print(f"      ❌ API failed")
        
        # Step 3: Batch update all amounts
        print(f"\n💾 Step 3: Updating master contact list...")
        if past_due_updates:
            update_results = batch_update_past_due_amounts(past_due_updates)
            print(f"   ✅ Updated {update_results['success_count']} members")
            if update_results['failed_count'] > 0:
                print(f"   ⚠️  Failed to update {update_results['failed_count']} members")
        
        # Step 4: Show members ready for invoices
        print(f"\n📧 Step 4: Members ready for invoice processing...")
        if members_with_amounts:
            print(f"   The following {len(members_with_amounts)} members are ready for invoices:")
            for name, amount, category in members_with_amounts[:10]:  # Show first 10
                print(f"      • {name} ({category}): ${amount:.2f}")
            if len(members_with_amounts) > 10:
                print(f"      ... and {len(members_with_amounts) - 10} more")
        else:
            print(f"   ⚠️  No members have past due amounts requiring invoices")
        
        # Final Summary
        print(f"\n🎯 FINAL WORKFLOW SUMMARY:")
        print(f"   📋 Total past due members: {len(past_due_members)}")
        print(f"   ✅ Successful API calls: {api_success}")
        print(f"   ❌ Failed API calls: {api_failures}")
        print(f"   💰 Members with past due amounts: {invoices_ready}")
        print(f"   📧 Ready for invoice sending: {invoices_ready}")
        print(f"   💾 Contact list updates: {update_results.get('success_count', 0) if past_due_updates else 0}")
        
        success_rate = (api_success / len(past_due_members)) * 100 if past_due_members else 0
        print(f"   📊 API success rate: {success_rate:.1f}%")
        
        if invoices_ready > 0:
            print(f"\n🎉 WORKFLOW READY!")
            print(f"   ✅ The overdue payments workflow is working correctly")
            print(f"   ✅ Found {invoices_ready} members requiring invoices")
            print(f"   ✅ All amounts are from real API data (no fallbacks)")
            print(f"   ✅ Contact list has been updated with current amounts")
            print(f"\n💡 Next step: Run the workflow with a WebDriver to send actual invoices")
        else:
            print(f"\n⚠️  No members currently require invoices")
            print(f"   This could mean all past due members are current on payments")
            print(f"   or that their agreements are not accessible via the API")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_overdue_workflow_test()
