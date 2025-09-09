"""
Overdue Payments Workflow
Handles processing of overdue member payments and invoice sending.
"""

from src.services.data.member_data import get_yellow_red_members, get_member_balance_from_contact_data, batch_update_past_due_amounts
from src.services.payments.square_client import create_overdue_payment_message_with_invoice
from src.services.clubos.messaging import send_clubos_message


def process_overdue_payments(driver):
    """
    Process overdue payments workflow - send invoices to yellow/red members.
    
    Args:
        driver: WebDriver instance for ClubOS operations
    
    Returns:
        bool: True if processing completed successfully
    """
    print("INFO: Processing overdue payments workflow...")
    
    try:
        # Get yellow/red members who need invoices
        past_due_members = get_yellow_red_members()
        
        if not past_due_members:
            print("INFO: No past due members found")
            return True
        
        print(f"INFO: Found {len(past_due_members)} past due members to process")
        
        invoices_sent = 0
        invoices_failed = 0
        skipped_no_data = 0
        past_due_updates = []  # Collect updates for batch processing
        
        for member in past_due_members:
            try:
                member_name = member['name']
                category = member['category']  # 'yellow' or 'red'
                
                # Get the actual past due amount for this specific member
                print(f"INFO: Fetching actual balance for {category} member: {member_name}")
                actual_amount_due = get_member_balance_from_contact_data(member)
                
                # Save the past due amount to our updates list (even if 0)
                past_due_updates.append((member_name, actual_amount_due))
                
                # ONLY process members with real API data - skip if no real amount
                if actual_amount_due <= 0:
                    print(f"⚠️  SKIPPED: {member_name} - No real past due amount from API")
                    skipped_no_data += 1
                    continue
                
                print(f"INFO: Processing {category} member: {member_name} (${actual_amount_due:.2f} past due)")
                
                # Create invoice and message with actual amount
                message, invoice_url = create_overdue_payment_message_with_invoice(
                    member_name=member_name,
                    membership_amount=actual_amount_due
                )
                
                if message and invoice_url:
                    # Send message via ClubOS
                    success = send_clubos_message(
                        driver=driver,
                        member_name=member_name, 
                        subject="⚠️ Overdue Payment - Action Required",
                        body=message
                    )
                    
                    if success:
                        print(f"✅ Invoice sent successfully to {member_name}")
                        print(f"   Invoice URL: {invoice_url}")
                        invoices_sent += 1
                    else:
                        print(f"❌ Failed to send message to {member_name}")
                        invoices_failed += 1
                else:
                    print(f"❌ Failed to create invoice for {member_name}")
                    invoices_failed += 1
                    
            except Exception as e:
                print(f"❌ Error processing member {member.get('name', 'Unknown')}: {e}")
                invoices_failed += 1
                continue
        
        # Batch update all past due amounts to master contact list
        print(f"\n💾 UPDATING MASTER CONTACT LIST...")
        if past_due_updates:
            update_results = batch_update_past_due_amounts(past_due_updates)
            print(f"   📝 Updated {update_results['success_count']} members with past due amounts")
            if update_results['failed_count'] > 0:
                print(f"   ⚠️  Failed to update {update_results['failed_count']} members")
        
        print(f"\n📊 OVERDUE PAYMENTS SUMMARY:")
        print(f"   ✅ Invoices sent: {invoices_sent}")
        print(f"   ❌ Failed: {invoices_failed}")
        print(f"   ⚠️  Skipped (no real API data): {skipped_no_data}")
        print(f"   📋 Total processed: {len(past_due_members)}")
        print(f"   💾 Past due amounts saved to master contact list")
        print(f"   💡 Only members with verified API balances received invoices")
        
        return invoices_sent > 0
        
    except Exception as e:
        print(f"❌ Error in overdue payments workflow: {e}")
        return False


def check_member_balance(member_name, member_id=None):
    """
    Check a specific member's balance using the ClubHub API.
    
    Args:
        member_name (str): Name of the member
        member_id (str): Optional member ID for API lookup
    
    Returns:
        float: The member's past due balance
    """
    from src.services.data.member_data import get_member_balance
    
    if member_id:
        balance = get_member_balance(member_id, member_name)
        print(f"Balance for {member_name}: ${balance:.2f}")
        return balance
    else:
        print(f"No member ID provided for {member_name} - cannot check balance")
        return 0.0


def test_past_due_amount_saving():
    """
    Test function to verify past due amount saving functionality.
    """
    print("🧪 TESTING PAST DUE AMOUNT SAVING...")
    
    # Test with some sample data
    test_updates = [
        ("Test Member 1", 45.50),
        ("Test Member 2", 89.99),
        ("Test Member 3", 0.00)
    ]
    
    print(f"   Testing batch update with {len(test_updates)} test entries...")
    
    # Note: This will only work if the members exist in the contact list
    result = batch_update_past_due_amounts(test_updates)
    
    print(f"   Results: {result['success_count']} successful, {result['failed_count']} failed")
    print("🧪 Test completed")
    
    return result
