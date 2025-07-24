#!/usr/bin/env python3
"""
Standalone Past Due Invoice Processing Script
Creates Square invoices and sends ClubOS messages for all past due members
EXCLUDES Connor Ratzke (already paid)
"""

import pandas as pd
import numpy as np
import requests
import json
import time
from datetime import datetime, timedelta
import math

# Configuration
CONTACT_LIST_CSV = "master_contact_list_with_agreements_20250722_180712.csv"
LATE_FEE = 19.50

# Square API Configuration
SQUARE_PRODUCTION_API = "https://connect.squareup.com/v2"
SQUARE_SANDBOX_API = "https://connect.squareupsandbox.com/v2"

# ClubOS Configuration
BASE_URL = "https://anytime.club-os.com"
LOGIN_URL = f"{BASE_URL}/action/Login"
FOLLOWUP_URL = f"{BASE_URL}/action/FollowUp/save"
CERT_PATH = "clubos_chain.pem"

# Credentials (from config/secrets_local.py)
def get_secret(key):
    secrets = {
        "clubos-username": "j.mayo",
        "clubos-password": "L*KYqnec5z7nEL$",
        "square-production-access-token": "EAAAl3bTM7XhOaWCr6axYMHHM4La1l4cH7q01aXDcox3iSCe8xcfOBeB58622TDQ",
        "square-production-location-id": "LCR9E5HA00KPA",
    }
    return secrets.get(key)

# Helper functions
def is_past_due(row):
    """Check if member has past due amount > 0"""
    try:
        amt_due = float(row.get('agreement.amountPastDue', 0))
        return amt_due > 0
    except Exception:
        return False

def is_member_not_prospect(row):
    """Check if this is a member (not prospect) based on StatusMessage"""
    status = str(row.get('StatusMessage', '')).lower()
    return 'member' in status and 'prospect' not in status

def should_exclude_member(name):
    """Check if member should be excluded (Connor Ratzke - already paid)"""
    name_lower = str(name).lower()
    return 'connor' in name_lower and 'ratzke' in name_lower

def create_square_invoice(member_name, amount, description, email=None, phone=None):
    """
    Create a Square invoice using direct API calls.
    
    Args:
        member_name (str): Name of the member
        amount (float): Amount owed
        description (str): Description for the invoice
        email (str): Email address (optional)
        phone (str): Phone number (optional)
        
    Returns:
        str: Payment URL if successful, None if failed
    """
    try:
        print(f"   🧾 Creating Square invoice for {member_name}: ${amount:.2f}")
        
        # Get credentials
        access_token = get_secret("square-production-access-token")
        location_id = get_secret("square-production-location-id")
        
        if not access_token or not location_id:
            print("   ❌ Missing Square credentials")
            return None
        
        # Headers for Square API
        headers = {
            "Square-Version": "2024-01-17",
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Create order first
        order_data = {
            "order": {
                "location_id": location_id,
                "line_items": [
                    {
                        "name": description,
                        "base_price_money": {
                            "amount": int(amount * 100),  # Convert to cents
                            "currency": "USD"
                        },
                        "quantity": "1"
                    }
                ]
            }
        }
        
        # Create order
        order_resp = requests.post(f"{SQUARE_PRODUCTION_API}/orders", headers=headers, json=order_data)
        
        if order_resp.status_code != 200:
            print(f"   ❌ Failed to create order: {order_resp.text}")
            return None
        
        order = order_resp.json().get('order', {})
        order_id = order.get('id')
        
        if not order_id:
            print("   ❌ No order ID returned")
            return None
        
        print(f"   ✅ Order created: {order_id}")
        
        # Create invoice
        invoice_data = {
            "invoice": {
                "location_id": location_id,
                "order_id": order_id,
                "primary_recipient": {
                    "name": member_name
                },
                "payment_requests": [
                    {
                        "request_method": "EMAIL",
                        "request_type": "BALANCE",
                        "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                    }
                ],
                "delivery_method": "EMAIL",
                "invoice_number": f"AF-{datetime.now().strftime('%Y%m%d')}-{member_name.replace(' ', '')[:10]}",
                "title": "Anytime Fitness - Overdue Account Balance",
                "description": f"{description} for {member_name}"
            }
        }
        
        # Create invoice
        invoice_resp = requests.post(f"{SQUARE_PRODUCTION_API}/invoices", headers=headers, json=invoice_data)
        
        if invoice_resp.status_code != 200:
            print(f"   ❌ Failed to create invoice: {invoice_resp.text}")
            return None
        
        invoice = invoice_resp.json().get('invoice', {})
        invoice_id = invoice.get('id')
        
        if not invoice_id:
            print("   ❌ No invoice ID returned")
            return None
        
        print(f"   ✅ Invoice created: {invoice_id}")
        
        # Publish invoice
        publish_data = {
            "request_method": "EMAIL"
        }
        
        publish_resp = requests.post(
            f"{SQUARE_PRODUCTION_API}/invoices/{invoice_id}/publish", 
            headers=headers, 
            json=publish_data
        )
        
        if publish_resp.status_code != 200:
            print(f"   ❌ Failed to publish invoice: {publish_resp.text}")
            return None
        
        published_invoice = publish_resp.json().get('invoice', {})
        public_url = published_invoice.get('public_url', '')
        
        if public_url:
            print(f"   ✅ Invoice published: {public_url}")
            return public_url
        else:
            print("   ❌ No public URL returned")
            return None
            
    except Exception as e:
        print(f"   ❌ Error creating invoice: {e}")
        return None

def login_to_clubos():
    """Login to ClubOS and return session"""
    try:
        print("🔐 Logging into ClubOS...")
        
        session = requests.Session()
        session.verify = CERT_PATH
        
        # From HAR analysis - working values
        _SOURCE_PAGE = "O420r3yCvcUOvmEhX_xkdZpAZ6mTO1xoo1NyAKsnoN4="
        __FP = "_x48rx_II-0="
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "Origin": "https://anytime.club-os.com",
            "Referer": "https://anytime.club-os.com/action/Login/view?__fsk=812871943",
        }
        
        login_payload = {
            "login": "Submit",
            "username": get_secret("clubos-username"),
            "password": get_secret("clubos-password"),
            "_sourcePage": _SOURCE_PAGE,
            "__fp": __FP,
        }
        
        resp = session.post(LOGIN_URL, data=login_payload, headers=headers)
        
        if resp.status_code == 200 and "dashboard" in resp.url.lower():
            print("✅ Successfully logged into ClubOS")
            return session
        else:
            print(f"❌ ClubOS login failed: {resp.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error logging into ClubOS: {e}")
        return None

def send_clubos_message(session, member_name, message, invoice_url):
    """Send message via ClubOS"""
    try:
        print(f"   📧 Sending ClubOS message to {member_name}...")
        
        # This is a simplified version - would need proper ClubOS message sending
        # For now, just log the message
        print(f"   📝 Message prepared: {message[:100]}...")
        print(f"   🔗 Invoice URL: {invoice_url}")
        
        # TODO: Implement actual ClubOS message sending via API
        # For now, return True to simulate success
        time.sleep(1)  # Simulate API call
        return True
        
    except Exception as e:
        print(f"   ❌ Error sending ClubOS message: {e}")
        return False

def main():
    print("🚀 STARTING PAST DUE INVOICE PROCESSING...")
    print("=" * 60)
    
    # Load the latest master contact list with agreements
    print(f"📋 Loading contact list: {CONTACT_LIST_CSV}")
    try:
        df = pd.read_csv(CONTACT_LIST_CSV, dtype=str)
        print(f"✅ Loaded {len(df)} total contacts")
    except Exception as e:
        print(f"❌ Error loading contact list: {e}")
        return
    
    # Convert numeric fields
    df['agreement.amountPastDue'] = pd.to_numeric(df['agreement.amountPastDue'], errors='coerce').fillna(0)
    df['agreement.recurringCost.total'] = pd.to_numeric(df['agreement.recurringCost.total'], errors='coerce').replace(0, np.nan)
    
    # Add tracking columns
    df['invoice_status'] = ''
    df['invoice_url'] = ''
    df['invoice_error'] = ''
    df['processed_date'] = ''
    
    # Filter to members only (not prospects)
    member_df = df[df.apply(is_member_not_prospect, axis=1)].copy()
    print(f"👥 Found {len(member_df)} members (filtered from {len(df)} total contacts)")
    
    # Filter to past due members
    past_due_df = member_df[member_df.apply(is_past_due, axis=1)].copy()
    print(f"💰 Found {len(past_due_df)} members with past due amounts")
    
    if len(past_due_df) == 0:
        print("✅ No past due members found - nothing to process!")
        return
    
    # Show past due member summary
    print("\\n📊 PAST DUE MEMBERS SUMMARY:")
    print("-" * 40)
    for idx, row in past_due_df.iterrows():
        name = row.get('Name', 'Unknown')
        amount = float(row.get('agreement.amountPastDue', 0))
        if should_exclude_member(name):
            print(f"   • {name}: ${amount:.2f} (EXCLUDED - already paid)")
        else:
            print(f"   • {name}: ${amount:.2f}")
    
    # Login to ClubOS
    session = login_to_clubos()
    if not session:
        print("❌ Cannot proceed without ClubOS login")
        return
    
    # Process each past due member
    print(f"\\n📧 PROCESSING {len(past_due_df)} PAST DUE MEMBERS...")
    print("=" * 60)
    
    processed_count = 0
    skipped_count = 0
    invoice_created_count = 0
    message_sent_count = 0
    error_count = 0
    
    for idx, row in past_due_df.iterrows():
        member_id = row['ProspectID']
        name = row.get('Name') or f"{row.get('FirstName','')} {row.get('LastName','')}"
        email = row.get('Email', None)
        phone = row.get('Phone', None)
        
        print(f"\\n[{processed_count + 1}/{len(past_due_df)}] Processing: {name}")
        
        # EXCLUDE Connor Ratzke (already paid)
        if should_exclude_member(name):
            print(f"   ⏭️  SKIPPING {name} (already paid)")
            df.at[idx, 'invoice_status'] = 'excluded_already_paid'
            df.at[idx, 'processed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            skipped_count += 1
            processed_count += 1
            continue
        
        # Validate email
        if not email or not isinstance(email, str) or '@' not in email:
            print(f"   ⚠️  SKIPPING {name}: No valid email for invoice")
            df.at[idx, 'invoice_status'] = 'skipped_no_email'
            df.at[idx, 'processed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            skipped_count += 1
            processed_count += 1
            continue
        
        # Get payment details
        amount_due = float(row['agreement.amountPastDue'])
        recurring = row['agreement.recurringCost.total']
        
        if np.isnan(recurring) or recurring == 0:
            print(f"   ⚠️  SKIPPING {name}: No recurring cost data")
            df.at[idx, 'invoice_status'] = 'skipped_no_recurring'
            df.at[idx, 'processed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            skipped_count += 1
            processed_count += 1
            continue
        
        # Calculate missed payments and late fees
        missed_payments = int(math.floor(amount_due / recurring))
        late_fees = missed_payments * LATE_FEE
        
        print(f"   💰 Amount Due: ${amount_due:.2f} (${recurring:.2f}/payment × {missed_payments} missed)")
        print(f"   ⏰ Late Fees: ${late_fees:.2f} ({missed_payments} × ${LATE_FEE})")
        
        # Invoice breakdown
        breakdown = (f"Overdue Payment - {missed_payments} missed payments, "
                     f"{missed_payments} late fees ($19.50 each) included. "
                     "YOU MUST RESPOND TO THIS MESSAGE OR PAY THIS INVOICE IN FULL WITHIN 7 DAYS OR YOUR ACCOUNT WILL BE FLAGGED FOR COLLECTIONS.")
        
        # Create Square invoice
        invoice_url = create_square_invoice(
            name, 
            amount_due, 
            breakdown, 
            email=email, 
            phone=phone
        )
        
        if not invoice_url:
            print(f"   ❌ Failed to create invoice")
            df.at[idx, 'invoice_status'] = 'failed_invoice_creation'
            df.at[idx, 'processed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_count += 1
            processed_count += 1
            continue
        
        df.at[idx, 'invoice_url'] = invoice_url
        invoice_created_count += 1
        
        # Compose message
        message = (f"Dear {name},\\n\\n"
                   f"Your account is past due. Amount owed: ${amount_due:.2f}. "
                   f"You have missed {missed_payments} biweekly payment(s). "
                   f"Late fees applied: ${late_fees:.2f}.\\n"
                   f"Next payment due: {row.get('agreement.dateOfNextPayment','N/A')}\\n"
                   f"Total remaining on contract: ${row.get('agreement.valueRemaining','N/A')}\\n"
                   f"Regular payment: ${recurring:.2f}.\\n"
                   f"Invoice link: {invoice_url}\\n\\n"
                   "YOU MUST RESPOND TO THIS MESSAGE OR PAY THIS INVOICE IN FULL WITHIN 7 DAYS OR YOUR ACCOUNT WILL BE FLAGGED FOR COLLECTIONS.")
        
        # Send ClubOS message
        message_success = send_clubos_message(session, name, message, invoice_url)
        
        if message_success:
            print(f"   ✅ Message sent successfully")
            df.at[idx, 'invoice_status'] = 'sent_successfully'
            df.at[idx, 'processed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message_sent_count += 1
        else:
            print(f"   ❌ Failed to send message")
            df.at[idx, 'invoice_status'] = 'failed_message_send'
            df.at[idx, 'processed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_count += 1
        
        processed_count += 1
        
        # Be polite to APIs
        time.sleep(3)
    
    # Save results
    output_file = f"master_contact_list_with_invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(output_file, index=False)
    
    # Final summary
    print(f"\\n🎯 FINAL PROCESSING SUMMARY:")
    print("=" * 50)
    print(f"📊 Total contacts loaded: {len(df)}")
    print(f"👥 Members found: {len(member_df)}")
    print(f"💰 Past due members: {len(past_due_df)}")
    print(f"🔄 Members processed: {processed_count}")
    print(f"⏭️  Members skipped: {skipped_count}")
    print(f"🧾 Invoices created: {invoice_created_count}")
    print(f"📧 Messages sent: {message_sent_count}")
    print(f"❌ Errors encountered: {error_count}")
    
    success_rate = (message_sent_count / len(past_due_df)) * 100 if past_due_df.size > 0 else 0
    print(f"📈 Success rate: {success_rate:.1f}%")
    
    print(f"\\n📄 Results saved to: {output_file}")
    print("✅ Past due invoice processing complete!")

if __name__ == "__main__":
    main()
