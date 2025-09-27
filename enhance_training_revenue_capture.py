#!/usr/bin/env python3
"""
Enhanced Training Revenue Data Capture Analysis

This script analyzes the current invoice data capture and proposes enhancements
to properly track monthly revenue from successful training package payments.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_current_invoice_data():
    """Analyze the current invoice data structure in package_details"""
    print("\n" + "="*80)
    print("💰 TRAINING REVENUE DATA ANALYSIS - INVOICE STRUCTURE")
    print("="*80)
    
    conn = sqlite3.connect('gym_bot.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get training clients with package details
    cursor.execute("""
        SELECT 
            member_name, 
            package_details, 
            past_due_amount, 
            total_past_due,
            payment_status,
            last_updated
        FROM training_clients 
        WHERE package_details IS NOT NULL 
        AND package_details != '' 
        AND package_details != '[]'
        ORDER BY total_past_due DESC
    """)
    
    clients = cursor.fetchall()
    
    print(f"\n📊 Found {len(clients)} training clients with package details")
    
    # Analyze invoice data structure
    total_agreements = 0
    agreements_with_invoices = 0
    total_past_due_invoices = 0
    total_current_invoices = 0
    total_invoice_count = 0
    
    missing_paid_invoice_data = []
    
    for client in clients:
        try:
            details = json.loads(client['package_details'])
            client_name = client['member_name']
            
            if isinstance(details, list):
                for package in details:
                    total_agreements += 1
                    
                    agreement_id = package.get('agreement_id')
                    package_name = package.get('package_name', 'Unknown')
                    invoice_count = package.get('invoice_count', 0)
                    payment_status = package.get('payment_status', 'Unknown')
                    amount_owed = package.get('amount_owed', 0)
                    
                    total_invoice_count += invoice_count
                    
                    if invoice_count > 0:
                        agreements_with_invoices += 1
                        
                        print(f"\n👤 {client_name} - Agreement {agreement_id}")
                        print(f"   📦 Package: {package_name}")
                        print(f"   💳 Total Invoices: {invoice_count}")
                        print(f"   💰 Amount Owed: ${amount_owed}")
                        print(f"   📊 Payment Status: {payment_status}")
                        
                        # Analyze billing status
                        billing_status = package.get('billing_status', {})
                        if billing_status:
                            past_invoices = billing_status.get('past', [])
                            current_invoices = billing_status.get('current', [])
                            
                            total_past_due_invoices += len(past_invoices)
                            total_current_invoices += len(current_invoices)
                            
                            if past_invoices:
                                print(f"   🔴 Past Due: {len(past_invoices)} invoices")
                                for invoice in past_invoices:
                                    if isinstance(invoice, dict):
                                        invoice_amount = invoice.get('amount', 0)
                                        due_date = invoice.get('dueDate', 'Unknown')
                                        print(f"       ${invoice_amount} due on {due_date}")
                            
                            if current_invoices:
                                print(f"   🟡 Current Unpaid: {len(current_invoices)} invoices")
                        
                        # Check for missing paid invoice data
                        if invoice_count > len(past_invoices) + len(current_invoices):
                            paid_invoice_count = invoice_count - len(past_invoices) - len(current_invoices)
                            missing_paid_invoice_data.append({
                                'client': client_name,
                                'agreement_id': agreement_id,
                                'package_name': package_name,
                                'total_invoices': invoice_count,
                                'past_due_invoices': len(past_invoices),
                                'current_invoices': len(current_invoices),
                                'likely_paid_invoices': paid_invoice_count
                            })
                            print(f"   ✅ Likely Paid: {paid_invoice_count} invoices (MISSING PAYMENT DATA)")
            
            elif isinstance(details, dict):
                # Handle single agreement format
                total_agreements += 1
                # ... similar logic for dict format
                
        except json.JSONDecodeError:
            print(f"⚠️ JSON decode error for {client['member_name']}")
        except Exception as e:
            print(f"⚠️ Error analyzing {client['member_name']}: {e}")
    
    print(f"\n📊 INVOICE DATA SUMMARY:")
    print(f"   Total Training Agreements: {total_agreements}")
    print(f"   Agreements with Invoices: {agreements_with_invoices}")
    print(f"   Total Invoice Count: {total_invoice_count}")
    print(f"   Past Due Invoices: {total_past_due_invoices}")
    print(f"   Current Unpaid Invoices: {total_current_invoices}")
    
    if missing_paid_invoice_data:
        print(f"\n💡 REVENUE OPPORTUNITY ANALYSIS:")
        print(f"   Clients with likely PAID invoices: {len(missing_paid_invoice_data)}")
        
        total_likely_paid = sum(item['likely_paid_invoices'] for item in missing_paid_invoice_data)
        print(f"   Total likely paid invoices: {total_likely_paid}")
        
        print(f"\n📋 CLIENTS WITH MISSING PAYMENT DATA:")
        for item in missing_paid_invoice_data[:10]:  # Show top 10
            print(f"   👤 {item['client']}: {item['likely_paid_invoices']} paid invoices (Agreement {item['agreement_id']})")
    
    conn.close()
    
    return {
        'total_agreements': total_agreements,
        'agreements_with_invoices': agreements_with_invoices,
        'total_invoice_count': total_invoice_count,
        'missing_paid_data': len(missing_paid_invoice_data),
        'likely_paid_invoices': sum(item['likely_paid_invoices'] for item in missing_paid_invoice_data) if missing_paid_invoice_data else 0
    }

def propose_revenue_enhancement():
    """Propose enhancements to capture paid invoice data for revenue calculations"""
    print("\n" + "="*80)
    print("🚀 PROPOSED ENHANCEMENTS FOR MONTHLY REVENUE TRACKING")
    print("="*80)
    
    print("""
💡 CURRENT LIMITATION:
   The package_details field only captures UNPAID invoice data (past due and current).
   To calculate monthly revenue, we need PAID invoice data with payment dates and amounts.

🎯 PROPOSED SOLUTION:
   Enhance ClubOS integration to capture complete invoice history including:
   
   1. PAID INVOICES with payment dates and amounts
   2. PAYMENT METHODS (credit card, ACH, cash, etc.)
   3. PAYMENT TRANSACTION DATES for monthly revenue analysis
   4. RECURRING PAYMENT SCHEDULES for future revenue projections

📋 IMPLEMENTATION STEPS:

   Step 1: Enhance ClubOSTrainingAPI.get_agreement_invoices_and_payments()
           - Capture ALL invoice statuses (not just unpaid)
           - Include payment dates for paid invoices
           - Store payment method information

   Step 2: Modify database schema to add paid_invoices field
           - Add 'paid_invoices' TEXT column to training_clients table
           - Store JSON array of paid invoice data with dates

   Step 3: Update training client sync to capture paid invoice data
           - Modify ClubOSIntegration.get_training_clients()
           - Store both unpaid AND paid invoice data

   Step 4: Enhance revenue analysis to calculate monthly totals
           - Parse paid invoice dates for monthly grouping
           - Calculate actual revenue per month from successful payments
           - Generate monthly revenue reports

🔧 TECHNICAL DETAILS:

   New package_details structure should include:
   ```json
   {
     "agreement_id": "12345",
     "package_name": "Personal Training Package",
     "invoice_count": 10,
     "paid_invoices": [
       {
         "id": "inv_001",
         "amount": 150.00,
         "payment_date": "2024-09-15T10:30:00Z",
         "payment_method": "Credit Card",
         "status": 1
       }
     ],
     "unpaid_invoices": [...],
     "past_due_invoices": [...]
   }
   ```

💰 EXPECTED OUTCOME:
   - Accurate monthly revenue calculations from training packages
   - Payment trend analysis
   - Revenue forecasting based on scheduled payments
   - Better financial reporting for training services
    """)

def main():
    """Main analysis function"""
    print("🔍 TRAINING REVENUE DATA ANALYSIS")
    print("=" * 80)
    
    # Analyze current invoice data
    analysis_results = analyze_current_invoice_data()
    
    # Show the gap in revenue tracking
    print(f"\n❌ REVENUE TRACKING GAP:")
    if analysis_results['likely_paid_invoices'] > 0:
        print(f"   We have {analysis_results['likely_paid_invoices']} likely paid invoices")
        print(f"   but NO payment dates or amounts for revenue calculation!")
        print(f"   This represents MISSING monthly revenue data that could be substantial.")
    
    # Propose enhancement solution
    propose_revenue_enhancement()
    
    print(f"\n✅ ANALYSIS COMPLETE")
    print(f"   Next step: Implement the proposed enhancements to capture paid invoice data")

if __name__ == "__main__":
    main()