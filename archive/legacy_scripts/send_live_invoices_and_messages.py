import pandas as pd
import numpy as np
from datetime import datetime
import math
import time
import os
import requests
from datetime import timedelta
import sys

# Add the current directory to Python path to access local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import credentials function
from config.secrets import get_secret

# Square API imports
from square.client import Square as SquareClient
from square.environment import SquareEnvironment
import json

CONTACT_LIST_CSV = "master_contact_list_with_agreements_20250722_180712.csv"
LATE_FEE = 19.50

# ClubOS configuration
BASE_URL = "https://anytime.club-os.com"
LOGIN_URL = f"{BASE_URL}/action/Login"
FOLLOWUP_URL = f"{BASE_URL}/action/FollowUp/save"
CERT_PATH = "clubos_chain.pem"

# Authentication
USERNAME = get_secret("clubos-username")
PASSWORD = get_secret("clubos-password")

# Use the captured _sourcePage and __fp values from HAR
_SOURCE_PAGE = "O420r3yCvcUOvmEhX_xkdZpAZ6mTO1xoo1NyAKsnoN4="
__FP = "_x48rx_II-0="

LOGIN_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
    "Origin": "https://anytime.club-os.com",
    "Referer": "https://anytime.club-os.com/action/Login/view?__fsk=812871943",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
}

def get_square_client():
    """Get configured Square client instance - from working script"""
    try:
        # Use PRODUCTION credentials - LIVE INVOICES
        access_token = get_secret("square-production-access-token")
        
        if not access_token:
            print("ERROR: Missing Square access token")
            return None
            
        return SquareClient(
            token=access_token,
            environment=SquareEnvironment.PRODUCTION
        )
    except Exception as e:
        print(f"ERROR: Failed to create Square client: {e}")
        return None

def create_square_invoice(member_name, amount, description="Overdue Payment", email=None, phone=None):
    """Create a Square invoice for a member with overdue payments - FIXED WITH CORRECT API STRUCTURE"""
    try:
        print(f"INFO: Creating Square invoice for {member_name}, amount: ${amount:.2f}")
        
        # Initialize Square client
        client = get_square_client()
        if not client:
            print("ERROR: Could not initialize Square client")
            return None
        
        # Get location ID - PRODUCTION
        location_id = get_secret("square-production-location-id")
        if not location_id:
            print("ERROR: Could not retrieve Square location ID")
            return None
        
        # Step 1: Create customer first (required for invoice)
        if not member_name or member_name.strip() == "":
            member_name = "Unknown Member"
            
        name_parts = member_name.split()
        first_name = name_parts[0] if name_parts else "Customer"
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        customer_data = {
            "given_name": first_name,
            "family_name": last_name,
        }
        
        # Only add phone for SMS delivery - don't add email
        if phone:
            customer_data["phone_number"] = phone
            
        customers_api = client.customers
        customer_result = customers_api.create(**customer_data)
        
        if customer_result.errors:
            print(f"ERROR: Failed to create customer: {customer_result.errors}")
            return None
            
        customer = customer_result.customer
        customer_id = customer.id if customer else None
        
        if not customer_id:
            print("ERROR: No customer ID returned")
            return None
            
        print(f"SUCCESS: Created customer {customer_id} for {member_name}")
        
        # Step 2: Create order
        order_data = {
            "location_id": location_id,
            "line_items": [
                {
                    "name": description[:100],  # Truncate description for line item name
                    "quantity": "1", 
                    "item_type": "ITEM",
                    "base_price_money": {
                        "amount": int(amount * 100),  # Convert to cents
                        "currency": "USD"
                    }
                }
            ]
        }
        
        orders_api = client.orders
        order_result = orders_api.create(order=order_data)
        
        if order_result.errors:
            print(f"ERROR: Failed to create order: {order_result.errors}")
            return None
        
        order = order_result.order
        order_id = order.id if order else None
        
        if not order_id:
            print("ERROR: No order ID returned")
            return None
            
        print(f"SUCCESS: Created order {order_id}")
        
        # Step 3: Create invoice with correct structure
        invoice_data = {
            "location_id": location_id,
            "order_id": order_id,
            "primary_recipient": {
                "customer_id": customer_id  # CORRECT: Use customer_id, not name
            },
            "payment_requests": [
                {
                    "request_type": "BALANCE",
                    "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                }
            ],
            "accepted_payment_methods": {
                "card": True,
                "square_gift_card": False,
                "bank_account": True,
                "buy_now_pay_later": False
            },
            "invoice_number": f"AF-{datetime.now().strftime('%Y%m%d')}-{member_name.replace(' ', '')[:10]}",
            "title": "Anytime Fitness - Overdue Account Balance",
            "description": f"{description}"
        }
        
        # Create the invoice
        invoices_api = client.invoices
        result = invoices_api.create(invoice=invoice_data)
        
        if result.errors:
            print(f"ERROR: Failed to create invoice: {result.errors}")
            return None
            
        invoice = result.invoice
        invoice_id = invoice.id if invoice else None
        invoice_version = invoice.version if invoice else None
        
        if not invoice_id:
            print("ERROR: No invoice ID returned")
            return None
            
        print(f"SUCCESS: Created invoice {invoice_id} for {member_name}")
        
        # Step 4: Publish the invoice to make it active
        try:
            publish_result = invoices_api.publish(
                invoice_id=invoice_id,
                version=invoice_version
            )
            
            if publish_result.errors:
                print(f"ERROR: Failed to publish invoice: {publish_result.errors}")
                return None
                
            published_invoice = publish_result.invoice
            invoice_url = published_invoice.public_url if published_invoice else None
            print(f"SUCCESS: Published invoice with URL: {invoice_url}")
            return invoice_url
                
        except Exception as publish_error:
            print(f"ERROR: Failed to publish invoice: {publish_error}")
            return None
            
    except Exception as e:
        print(f"ERROR: Exception during invoice creation: {e}")
        return None

def login_and_get_session():
    session = requests.Session()
    session.verify = CERT_PATH
    login_payload = {
        "login": "Submit",
        "username": USERNAME,
        "password": PASSWORD,
        "_sourcePage": _SOURCE_PAGE,
        "__fp": __FP,
    }
    resp = session.post(LOGIN_URL, data=login_payload, headers=LOGIN_HEADERS)
    print(f"Login status code: {resp.status_code}")
    if resp.status_code == 200 and "Dashboard" in resp.text:
        print("✅ Logged in to ClubOS successfully.")
        return session
    print("❌ Login failed.")
    return None

def send_invoice_via_clubos(session, invoice_url, member_name, email, phone, amount, description):
    print(f"📤 Sending invoice via ClubOS for {member_name}...")
    email_subject = f"Invoice - {description}"
    email_message = f"""
<p>Hi {member_name}!</p>
<p>This is an invoice from the Gym Bot automation system.</p>
<p><strong>Amount:</strong> ${amount:.2f}</p>
<p><strong>Description:</strong> {description}</p>
<p>Please click the link below to pay:</p>
<p><a href=\"{invoice_url}\">{invoice_url}</a></p>
<p>Thanks,<br>Gym Bot AI</p>
"""
    text_message = f"Invoice: ${amount:.2f} - Pay here: {invoice_url}"
    payload = {
        "followUpStatus": "1",
        "followUpType": "3",
        "memberSalesFollowUpStatus": "6",
        "followUpLog.tfoUserId": "184027841",
        "followUpLog.outcome": "2",
        "emailSubject": email_subject,
        "emailMessage": email_message,
        "textMessage": text_message,
        "event.createdFor.tfoUserId": "187032782",
        "event.eventType": "ORIENTATION",
        "duration": "2",
        "event.remindAttendeesMins": "120",
        "followUpUser.tfoUserId": "184027841",
        "followUpUser.role.id": "7",
        "followUpUser.clubId": "291",
        "followUpUser.clubLocationId": "3586",
        "followUpLog.followUpAction": "2",
        "memberStudioSalesDefaultAccount": "187032782",
        "memberStudioSupportDefaultAccount": "187032782",
        "ptSalesDefaultAccount": "187032782",
        "ptSupportDefaultAccount": "187032782",
        "followUpUser.firstName": member_name.split()[0],
        "followUpUser.lastName": member_name.split()[-1] if len(member_name.split()) > 1 else "",
        "followUpUser.email": email,
        "followUpUser.mobilePhone": phone or "",
    }
    resp = session.post(FOLLOWUP_URL, data=payload)
    print(f"Email request status: {resp.status_code}")
    print(f"Email response: {resp.text[:200]}")
    payload["followUpLog.followUpAction"] = "3"
    resp2 = session.post(FOLLOWUP_URL, data=payload)
    print(f"SMS request status: {resp2.status_code}")
    print(f"SMS response: {resp2.text[:200]}")
    return resp.status_code == 200 and resp2.status_code == 200

# Helper to determine if a member is past due (yellow/red)
def is_past_due(row):
    try:
        amt_due = float(row.get('agreement_amountPastDue', 0))
        return amt_due > 0
    except Exception:
        return False

# Helper to check if member should be excluded
def should_exclude_member(name):
    """Check if member should be excluded (Connor Ratzke - already paid)"""
    name_lower = str(name).lower()
    return 'connor' in name_lower and 'ratzke' in name_lower

def parse_recurring_cost(recurring_cost_str):
    """Parse the recurring cost from the JSON-like string format"""
    try:
        if pd.isna(recurring_cost_str) or not recurring_cost_str:
            return 0.0
        
        # Handle if it's already a number
        if isinstance(recurring_cost_str, (int, float)):
            return float(recurring_cost_str)
        
        # Parse the JSON-like string
        import ast
        cost_dict = ast.literal_eval(str(recurring_cost_str))
        if isinstance(cost_dict, dict) and 'total' in cost_dict:
            return float(cost_dict['total'])
        
        return 0.0
    except Exception:
        return 0.0

def main():
    df = pd.read_csv(CONTACT_LIST_CSV, dtype=str)
    df['agreement_amountPastDue'] = pd.to_numeric(df['agreement_amountPastDue'], errors='coerce').fillna(0)
    
    # Skip ClubOS login since we only need Square invoices
    print("🚀 Starting Square invoice processing...")
    
    # List to track processing results
    results = []
    
    for idx, row in df.iterrows():
        amount_due = float(row.get('agreement_amountPastDue', 0))
        if amount_due <= 0:
            continue
            
        name = row.get('Name') or f"{row.get('firstName','')} {row.get('lastName','')}"
        name = name.strip()
        
        if not name:
            print(f"[SKIP] Row {idx}: No valid name found.")
            continue
        
        if should_exclude_member(name):
            print(f"[SKIP] {name}: Excluded (Connor Ratzke)")
            continue
            
        email = row.get('Email') or row.get('email')
        phone = row.get('mobilePhone')  # Only use mobile phone numbers
        
        if not phone or not isinstance(phone, str) or len(phone.strip()) < 10:
            print(f"[SKIP] {name}: No valid mobile phone number, cannot send SMS invoice.")
            continue
            
        recurring = parse_recurring_cost(row.get('agreement_recurringCost'))
        if recurring == 0:
            print(f"[SKIP] {name}: No recurring cost.")
            continue
        missed_payments = int(math.floor(amount_due / recurring))
        late_fees = missed_payments * LATE_FEE
        total_amount_due = amount_due + late_fees
        breakdown = (f"Overdue Payment - {missed_payments} missed payments, "
                     f"{missed_payments} late fees ($19.50 each) included. "
                     "YOU MUST RESPOND TO THIS MESSAGE OR PAY THIS INVOICE IN FULL WITHIN 7 DAYS OR YOUR ACCOUNT WILL BE FLAGGED FOR COLLECTIONS.")
        
        # Record the member details for CSV output
        result = {
            'name': name,
            'email': email,
            'phone': phone,
            'amount_due': amount_due,
            'recurring_cost': recurring,
            'missed_payments': missed_payments,
            'late_fees': late_fees,
            'total_amount_due': total_amount_due,
            'breakdown': breakdown,
            'status': 'PENDING'
        }
        results.append(result)
        
        print(f"[READY] {name}: ${total_amount_due:.2f} ({missed_payments} payments + ${late_fees:.2f} late fees)")
        
        # Create Square invoice
        try:
            invoice_url = create_square_invoice(
                member_name=name,
                amount=total_amount_due,
                description=breakdown,
                email=email,
                phone=phone
            )
            if not invoice_url:
                print(f"[FAIL] {name}: Failed to create invoice.")
                result['status'] = 'SQUARE_FAILED'
                continue
            result['invoice_url'] = invoice_url
            result['status'] = 'INVOICE_SENT'
            print(f"✅ {name}: Invoice created and sent successfully!")
        except Exception as e:
            print(f"[FAIL] {name}: Exception creating invoice: {e}")
            result['status'] = 'SQUARE_ERROR'
            continue
        
        time.sleep(1)
    
    # Save results to CSV
    if results:
        results_df = pd.DataFrame(results)
        output_file = f"overdue_members_for_square_invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        results_df.to_csv(output_file, index=False)
        print(f"\n📋 Saved {len(results)} members to process: {output_file}")
        print(f"Total amount to collect: ${sum(r['total_amount_due'] for r in results):.2f}")
    else:
        print("No members found for invoice processing.")
        
    print("Processing complete.")

if __name__ == "__main__":
    main() 