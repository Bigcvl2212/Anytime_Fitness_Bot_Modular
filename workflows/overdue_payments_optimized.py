"""
Optimized Overdue Payments Workflow - BATCH PROCESSING
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional

from src.services.data.member_data import get_yellow_red_members, get_member_balance_from_contact_data
from src.services.payments.square_client_fixed import create_square_invoice
from src.services.clubos.messaging import send_clubos_message
from ..core.driver import login_to_clubos
from ..config.constants import LATE_FEE_AMOUNT


def get_members_with_balances() -> List[Dict]:
    """
    Get yellow/red members and fetch their actual past due amounts from API.
    
    Returns:
        List of member dictionaries with actual past due amounts
    """
    print("📋 GATHERING MEMBER DATA WITH REAL BALANCES...")
    print("=" * 50)
    
    # Get list of yellow/red members
    members = get_yellow_red_members()
    if not members:
        print("❌ No past due members found")
        return []
    
    print(f"✅ Found {len(members)} past due members")
    
    # Fetch real balances for each member
    members_with_balances = []
    successful_fetches = 0
    failed_fetches = 0
    
    for i, member in enumerate(members, 1):
        member_name = member['name']
        
        # EXCLUDE Connor Ratzke (already paid)
        if 'connor' in member_name.lower() and 'ratzke' in member_name.lower():
            print(f"\n[{i}/{len(members)}] ⏭️  Skipping {member_name} (already paid)")
            continue
            
        print(f"\n[{i}/{len(members)}] Fetching balance for {member_name}...")
        
        try:
            # DEBUG: Check what member data we have
            print(f"   DEBUG: Member data for {member_name}:")
            print(f"     - member_id: '{member.get('member_id', 'MISSING')}'")
            print(f"     - name: '{member.get('name', 'MISSING')}'")
            print(f"     - email: '{member.get('email', 'MISSING')}'")
            
            # Convert old format to new format for balance fetch
            member_data = {
                'Name': member['name'],
                'member_id': member['member_id'],  # FIXED: Use 'member_id' key that the function expects
                'ProspectID': member['member_id'],  # Keep for backward compatibility
                'Email': member['email'],
                'Phone': member['phone'],
                'StatusMessage': member['status_message']
            }
            
            past_due_amount = get_member_balance_from_contact_data(member_data)
            
            if past_due_amount and past_due_amount > 0:
                # Add balance info to member with proper formatting
                member_with_balance = {
                    'past_due_amount': past_due_amount,
                    'full_name': member_name,
                    'type': member['category'],  # 'yellow' or 'red'
                    'member_data': member_data,  # Store the properly formatted data
                    # Keep original fields for compatibility
                    'name': member['name'],
                    'member_id': member['member_id'],
                    'email': member['email'],
                    'phone': member['phone'],
                    'status_message': member['status_message'],
                    'category': member['category']
                }
                
                members_with_balances.append(member_with_balance)
                successful_fetches += 1
                print(f"✅ {member_name}: ${past_due_amount:.2f}")
            else:
                failed_fetches += 1
                print(f"⚠️  {member_name}: No balance or API error")
                
        except Exception as e:
            failed_fetches += 1
            print(f"❌ {member_name}: Error fetching balance - {e}")
    
    print(f"\n📊 BALANCE FETCH SUMMARY:")
    print(f"   ✅ Successful: {successful_fetches}")
    print(f"   ❌ Failed: {failed_fetches}")
    print(f"   📝 Actionable members: {len(members_with_balances)}")
    
    return members_with_balances


def create_invoice_batch(members: List[Dict]) -> Dict[str, Dict]:
    """
    Create Square invoices for all members upfront and save results.
    
    Args:
        members: List of member dictionaries with past due amounts
        
    Returns:
        Dict mapping member names to invoice data
    """
    print(f"\n🏗️  BATCH CREATING INVOICES FOR {len(members)} MEMBERS...")
    print("=" * 60)
    
    invoice_batch = {}
    successful_invoices = 0
    failed_invoices = 0
    
    for i, member in enumerate(members, 1):
        member_name = member['full_name']
        past_due_amount = member['past_due_amount']
        member_type = member['type']  # 'yellow' or 'red'
        
        # EXCLUDE Connor Ratzke (already paid) 
        if 'connor' in member_name.lower() and 'ratzke' in member_name.lower():
            print(f"\n[{i}/{len(members)}] ⏭️  Skipping {member_name} (already paid)")
            continue
        
        print(f"\n[{i}/{len(members)}] Creating invoice for {member_name} (${past_due_amount:.2f})...")
        
        # Calculate total amount with late fee
        total_amount = past_due_amount + LATE_FEE_AMOUNT
        
        # Create Square invoice
        invoice_url = create_square_invoice(
            member_name=member_name,
            amount=total_amount,
            description=f"Overdue Membership Payment + Late Fee"
        )
        
        if invoice_url:
            # Save invoice data for later messaging
            invoice_batch[member_name] = {
                'member_data': member,
                'past_due_amount': past_due_amount,
                'late_fee': LATE_FEE_AMOUNT,
                'total_amount': total_amount,
                'invoice_url': invoice_url,
                'member_type': member_type,
                'status': 'ready_to_send'
            }
            successful_invoices += 1
            print(f"✅ Invoice created for {member_name}")
        else:
            # Save failed invoice for tracking
            invoice_batch[member_name] = {
                'member_data': member,
                'past_due_amount': past_due_amount,
                'status': 'failed_to_create',
                'error': 'Invoice creation failed'
            }
            failed_invoices += 1
            print(f"❌ Failed to create invoice for {member_name}")
    
    print(f"\n📊 INVOICE BATCH CREATION SUMMARY:")
    print(f"   ✅ Successful: {successful_invoices}")
    print(f"   ❌ Failed: {failed_invoices}")
    print(f"   📝 Total: {len(members)}")
    
    # Save batch to file for recovery/debugging
    save_invoice_batch_to_file(invoice_batch)
    
    return invoice_batch


def save_invoice_batch_to_file(invoice_batch: Dict) -> None:
    """Save invoice batch to JSON file for recovery."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"invoice_batch_{timestamp}.json"
        filepath = os.path.join("logs", filename)
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        # Convert to JSON serializable format
        json_batch = {}
        for member_name, data in invoice_batch.items():
            json_batch[member_name] = {
                k: v for k, v in data.items() 
                if k != 'member_data'  # Skip complex member data
            }
            json_batch[member_name]['member_name'] = member_name
        
        with open(filepath, 'w') as f:
            json.dump(json_batch, f, indent=2)
        
        print(f"💾 Invoice batch saved to: {filepath}")
    except Exception as e:
        print(f"⚠️  Failed to save invoice batch: {e}")


def send_invoice_messages_batch(driver, invoice_batch: Dict) -> Tuple[int, int]:
    """
    Send messages for all created invoices using authenticated ClubOS session.
    
    Args:
        driver: Authenticated WebDriver session
        invoice_batch: Dictionary of invoice data
        
    Returns:
        Tuple of (successful_sends, failed_sends)
    """
    print(f"\n📧 BATCH SENDING MESSAGES...")
    print("=" * 60)
    
    successful_sends = 0
    failed_sends = 0
    
    # Filter to only invoices that are ready to send
    ready_invoices = {
        name: data for name, data in invoice_batch.items() 
        if data.get('status') == 'ready_to_send'
    }
    
    print(f"📨 Sending messages for {len(ready_invoices)} invoices...")
    
    for i, (member_name, invoice_data) in enumerate(ready_invoices.items(), 1):
        print(f"\n[{i}/{len(ready_invoices)}] Sending message to {member_name}...")
        
        try:
            # Prepare message with invoice link
            message = create_message_with_invoice_link(
                member_name=member_name,
                past_due_amount=invoice_data['past_due_amount'],
                late_fee=invoice_data['late_fee'],
                total_amount=invoice_data['total_amount'],
                invoice_url=invoice_data['invoice_url']
            )
            
            # Send message via ClubOS
            success = send_clubos_message(
                driver=driver,
                member_name=invoice_data['member_data']['Name'],
                subject="Anytime Fitness - Overdue Account",
                body=message
            )
            
            if success:
                successful_sends += 1
                print(f"✅ Message sent to {member_name}")
            else:
                failed_sends += 1
                print(f"❌ Failed to send message to {member_name}")
                
        except Exception as e:
            failed_sends += 1
            print(f"❌ Exception sending message to {member_name}: {e}")
    
    print(f"\n📊 MESSAGE SENDING SUMMARY:")
    print(f"   ✅ Successful: {successful_sends}")
    print(f"   ❌ Failed: {failed_sends}")
    print(f"   📝 Total Attempted: {len(ready_invoices)}")
    
    return successful_sends, failed_sends


def create_message_with_invoice_link(member_name: str, past_due_amount: float, 
                                   late_fee: float, total_amount: float, 
                                   invoice_url: str) -> str:
    """Create formatted message with invoice link."""
    
    message = f"""Hi {member_name},

Your Anytime Fitness membership account has a past due balance of ${past_due_amount:.2f}.

To avoid further late fees and potential suspension of your membership, please pay your balance immediately.

Current charges:
• Past due amount: ${past_due_amount:.2f}
• Late fee: ${late_fee:.2f}
• Total amount due: ${total_amount:.2f}

Pay securely online: {invoice_url}

If you have questions about your account, please contact us immediately.

Thank you,
Anytime Fitness Fond du Lac"""

    return message


def process_overdue_payments_optimized(driver) -> bool:
    """
    Optimized overdue payments workflow with batch processing.
    
    Args:
        driver: WebDriver instance (will be used for ClubOS after login)
        
    Returns:
        bool: True if workflow completed successfully
    """
    try:
        print("🚀 STARTING OPTIMIZED OVERDUE PAYMENTS WORKFLOW...")
        print("=" * 80)
        
        # Step 1: Get all yellow/red members with past due amounts
        print("\n📋 STEP 1: GATHERING MEMBER DATA...")
        members_with_balances = get_members_with_balances()
        
        if not members_with_balances:
            print("❌ No past due members found")
            return False
        
        print(f"✅ Found {len(members_with_balances)} members with past due balances")
        
        # Step 2: Create all invoices upfront
        print(f"\n💰 STEP 2: BATCH CREATING SQUARE INVOICES...")
        invoice_batch = create_invoice_batch(members_with_balances)
        
        successful_invoices = len([
            data for data in invoice_batch.values() 
            if data.get('status') == 'ready_to_send'
        ])
        
        if successful_invoices == 0:
            print("❌ No invoices were created successfully")
            return False
        
        print(f"✅ Created {successful_invoices} invoices successfully")
        
        # Step 3: Login to ClubOS
        print(f"\n🔐 STEP 3: LOGGING INTO CLUBOS...")
        authenticated = login_to_clubos(driver)
        
        if not authenticated:
            print("❌ Failed to login to ClubOS")
            print("💡 Invoices have been created and saved. You can retry messaging later.")
            return False
        
        print("✅ Successfully logged into ClubOS")
        
        # Step 4: Send all messages with invoice links
        print(f"\n📧 STEP 4: BATCH SENDING MESSAGES...")
        successful_sends, failed_sends = send_invoice_messages_batch(driver, invoice_batch)
        
        # Final summary
        print(f"\n🎯 FINAL WORKFLOW SUMMARY:")
        print("=" * 50)
        print(f"📊 Members processed: {len(members_with_balances)}")
        print(f"💰 Invoices created: {successful_invoices}")
        print(f"📧 Messages sent: {successful_sends}")
        print(f"❌ Message failures: {failed_sends}")
        
        success_rate = (successful_sends / len(members_with_balances)) * 100 if members_with_balances else 0
        print(f"📈 Overall success rate: {success_rate:.1f}%")
        
        return success_rate > 50  # Consider successful if >50% complete
        
    except Exception as e:
        print(f"❌ WORKFLOW ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
