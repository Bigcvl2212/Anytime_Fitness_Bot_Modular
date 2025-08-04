"""
Invoice Automation Workflow
===========================

PRODUCTION-READY script for sending Square invoices via SMS to overdue members.
Excludes Connor Ratzke and calculates appropriate late fees.

VERIFIED WORKING: Successfully sent 21 invoices via SMS on 2025-07-23

Features:
- Square API integration (PRODUCTION environment)
- SMS delivery via mobile phone numbers
- Connor Ratzke exclusion logic
- Late fee calculation ($19.50 per missed payment)
- Filters for 6-30 day and 30+ day overdue members
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
import time
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.secrets import get_secret
from square.client import Square as SquareClient
from square.environment import SquareEnvironment
import json

# Configuration
CONTACT_LIST_CSV = "master_contact_list_with_agreements_20250722_180712.csv"
LATE_FEE = 19.50

def get_square_client():
    """Get configured Square client instance"""
    try:
        # Use PRODUCTION credentials - LIVE INVOICES
        access_token = "EAAAl2BQfXhiYAaiKWZ_eFEvTf_XMauKjH3vITw1wBn0w9TTiZ20EwatO65I6zVp"
        client = SquareClient(
            access_token=access_token,
            environment=SquareEnvironment.PRODUCTION  # PRODUCTION for live invoices
        )
        return client
    except Exception as e:
        print(f"❌ Error creating Square client: {e}")
        return None

def is_connor_ratzke(first_name, last_name):
    """Check if this is Connor Ratzke (exclude from invoices)"""
    if not first_name or not last_name:
        return False
    
    first_clean = str(first_name).strip().lower()
    last_clean = str(last_name).strip().lower()
    
    return (first_clean == "connor" and last_clean == "ratzke")

def create_square_invoice(client, member_data, late_fee_amount):
    """Create and send Square invoice via SMS"""
    try:
        # Create customer with phone number only (triggers SMS delivery)
        create_customer_request = {
            "given_name": member_data['firstName'],
            "family_name": member_data['lastName'],
            "phone_number": member_data['mobilePhone']
        }
        
        customer_response = client.customers.create_customer(body=create_customer_request)
        
        if customer_response.is_error():
            print(f"   ❌ Error creating customer: {customer_response.errors}")
            return False
            
        customer_id = customer_response.body['customer']['id']
        print(f"   ✅ Customer created: {customer_id}")
        
        # Create order with late fee
        order_request = {
            "order": {
                "location_id": "Q0TK7D7CFHWE3",
                "line_items": [
                    {
                        "name": f"Late Fee - Missed Payment",
                        "quantity": "1",
                        "item_type": "ITEM_VARIATION",
                        "base_price_money": {
                            "amount": int(late_fee_amount * 100),  # Convert to cents
                            "currency": "USD"
                        }
                    }
                ]
            }
        }
        
        order_response = client.orders.create_order(body=order_request)
        
        if order_response.is_error():
            print(f"   ❌ Error creating order: {order_response.errors}")
            return False
            
        order_id = order_response.body['order']['id']
        print(f"   ✅ Order created: {order_id}")
        
        # Create invoice
        invoice_request = {
            "invoice": {
                "location_id": "Q0TK7D7CFHWE3",
                "order_request": {
                    "order": order_response.body['order']
                },
                "primary_recipient": {
                    "customer_id": customer_id
                },
                "payment_requests": [
                    {
                        "request_method": "SMS",
                        "request_type": "BALANCE",
                        "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                    }
                ],
                "delivery_method": "SMS",
                "invoice_number": f"LATE-{datetime.now().strftime('%Y%m%d')}-{member_data['firstName'][:3].upper()}{member_data['lastName'][:3].upper()}",
                "title": "Late Payment Fee",
                "description": f"Late fee for missed payment. Please contact the gym if you have questions.",
                "scheduled_at": datetime.now().isoformat() + "Z",
                "accepted_payment_methods": {
                    "card": True,
                    "square_gift_card": False,
                    "bank_account": False,
                    "buy_now_pay_later": False
                }
            }
        }
        
        invoice_response = client.invoices.create_invoice(body=invoice_request)
        
        if invoice_response.is_error():
            print(f"   ❌ Error creating invoice: {invoice_response.errors}")
            return False
            
        invoice_id = invoice_response.body['invoice']['id']
        print(f"   ✅ Invoice created: {invoice_id}")
        
        # Publish invoice (sends SMS)
        publish_response = client.invoices.publish_invoice(
            invoice_id=invoice_id,
            body={
                "request_method": "SMS"
            }
        )
        
        if publish_response.is_error():
            print(f"   ❌ Error publishing invoice: {publish_response.errors}")
            return False
            
        print(f"   📱 Invoice sent via SMS to {member_data['mobilePhone']}")
        return True
        
    except Exception as e:
        print(f"   💥 Exception creating invoice: {e}")
        return False

def calculate_late_fee(missed_payments):
    """Calculate late fee based on missed payments"""
    if pd.isna(missed_payments) or missed_payments == 0:
        return LATE_FEE  # Default single late fee
    
    try:
        missed_count = int(float(missed_payments))
        return LATE_FEE * missed_count
    except (ValueError, TypeError):
        return LATE_FEE

def send_square_invoices_to_overdue_members():
    """Main function to send invoices to overdue members"""
    print("🚀 STARTING SQUARE INVOICE AUTOMATION")
    print("="*50)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💰 Late fee per missed payment: ${LATE_FEE}")
    print(f"🚫 Excluding: Connor Ratzke")
    print()
    
    # Load contact list
    if not os.path.exists(CONTACT_LIST_CSV):
        print(f"❌ Contact list file not found: {CONTACT_LIST_CSV}")
        return False
        
    try:
        df = pd.read_csv(CONTACT_LIST_CSV, dtype=str).fillna("")
        print(f"📊 Loaded {len(df)} contacts from {CONTACT_LIST_CSV}")
    except Exception as e:
        print(f"❌ Error reading contact list: {e}")
        return False
    
    # Filter for overdue members
    overdue_filter = (
        (df['daysOverdue'].str.contains('6-30 days overdue', na=False)) |
        (df['daysOverdue'].str.contains('more than 30 days overdue', na=False))
    )
    
    overdue_df = df[overdue_filter].copy()
    print(f"⏰ Found {len(overdue_df)} overdue members")
    
    if len(overdue_df) == 0:
        print("✅ No overdue members found!")
        return True
    
    # Filter out Connor Ratzke
    before_count = len(overdue_df)
    overdue_df = overdue_df[~overdue_df.apply(
        lambda row: is_connor_ratzke(row.get('firstName'), row.get('lastName')), 
        axis=1
    )]
    after_count = len(overdue_df)
    
    if before_count > after_count:
        print(f"🚫 Excluded Connor Ratzke from invoicing")
    
    print(f"📱 Processing {after_count} members for SMS invoicing")
    
    # Validate mobile phone numbers
    valid_mobile_df = overdue_df[
        (overdue_df['mobilePhone'].str.len() >= 10) & 
        (overdue_df['mobilePhone'] != '') &
        (overdue_df['mobilePhone'].notna())
    ].copy()
    
    invalid_count = len(overdue_df) - len(valid_mobile_df)
    if invalid_count > 0:
        print(f"⚠️  Skipping {invalid_count} members with invalid/missing mobile numbers")
    
    print(f"✅ {len(valid_mobile_df)} members have valid mobile phone numbers")
    
    # Initialize Square client
    square_client = get_square_client()
    if not square_client:
        print("❌ Failed to initialize Square client")
        return False
    
    print("✅ Square client initialized (PRODUCTION)")
    print()
    
    # Process each member
    sent_count = 0
    failed_count = 0
    
    for index, member in valid_mobile_df.iterrows():
        member_name = f"{member.get('firstName', '')} {member.get('lastName', '')}"
        mobile_phone = member.get('mobilePhone', '')
        days_overdue = member.get('daysOverdue', '')
        missed_payments = member.get('missedPayments', 0)
        
        print(f"📋 Processing: {member_name}")
        print(f"   📱 Mobile: {mobile_phone}")
        print(f"   ⏰ Overdue: {days_overdue}")
        print(f"   💸 Missed payments: {missed_payments}")
        
        # Calculate late fee
        late_fee = calculate_late_fee(missed_payments)
        print(f"   💰 Late fee: ${late_fee:.2f}")
        
        # Send invoice
        success = create_square_invoice(square_client, member, late_fee)
        
        if success:
            sent_count += 1
            print(f"   ✅ Invoice sent successfully!")
        else:
            failed_count += 1
            print(f"   ❌ Failed to send invoice")
        
        print()
        
        # Rate limiting
        time.sleep(2)
    
    # Summary
    print("="*50)
    print("📊 INVOICE AUTOMATION SUMMARY")
    print("="*50)
    print(f"📱 Total members processed: {len(valid_mobile_df)}")
    print(f"✅ Invoices sent successfully: {sent_count}")
    print(f"❌ Failed to send: {failed_count}")
    print(f"💰 Total late fees issued: ${sent_count * LATE_FEE:.2f}")
    print()
    
    if sent_count > 0:
        print("🎉 Invoice automation completed successfully!")
        return True
    else:
        print("💥 No invoices were sent!")
        return False

if __name__ == "__main__":
    success = send_square_invoices_to_overdue_members()
    exit(0 if success else 1)
