import pandas as pd
import numpy as np
from datetime import datetime
import math
import time
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the square client functions
try:
    from src.services.payments.square_client_fixed import create_square_invoice
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative import method...")
    import importlib.util
    spec = importlib.util.spec_from_file_location("square_client_fixed", "services/payments/square_client_fixed.py")
    square_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(square_module)
    create_square_invoice = square_module.create_square_invoice

# ClubOS messaging removed - Square handles invoice delivery

# Use the latest master contact list with agreements data
CONTACT_LIST_CSV = "master_contact_list_with_agreements_20250722_180712.csv"
LATE_FEE = 19.50

# Helper to determine if a member is past due based on status message (yellow/red)
def is_past_due_status(row):
    """Check status message for past due conditions"""
    status_message = str(row.get('agreement_statusMessage', ''))
    return 'Past Due more than 30 days' in status_message or 'Past Due 6-30 days' in status_message

def is_member_not_prospect(row):
    """Check if this is a member (not prospect) based on statusMessage"""
    status = str(row.get('statusMessage', '')).lower()
    # Include regular members and past due members
    return ('member' in status and 'prospect' not in status) or 'past due' in status

def should_exclude_member(name):
    """Check if member should be excluded (Connor Ratzke - already paid)"""
    name_lower = str(name).lower()
    return 'connor' in name_lower and 'ratzke' in name_lower

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
    
    # Convert numeric fields (using correct column names)
    df['agreement_amountPastDue'] = pd.to_numeric(df['agreement_amountPastDue'], errors='coerce').fillna(0)
    
    # Parse the recurring cost from JSON string
    def parse_recurring_cost(cost_str):
        try:
            import ast
            if pd.isna(cost_str) or cost_str == '':
                return np.nan
            # Convert string representation of dict to actual dict
            cost_dict = ast.literal_eval(str(cost_str))
            return float(cost_dict.get('total', 0))
        except:
            return np.nan
    
    df['agreement_recurringCost_parsed'] = df['agreement_recurringCost'].apply(parse_recurring_cost)
    
    # Add tracking columns
    df['invoice_status'] = ''
    df['invoice_url'] = ''
    df['invoice_error'] = ''
    df['processed_date'] = ''
    
    # Filter to members only (not prospects)
    member_df = df[df.apply(is_member_not_prospect, axis=1)].copy()
    print(f"👥 Found {len(member_df)} members (filtered from {len(df)} total contacts)")
    
# Filter to past due members by status message
    past_due_df = member_df[member_df.apply(is_past_due_status, axis=1)].copy()
    print(f"💰 Found {len(past_due_df)} members with past due status")
    
    if len(past_due_df) == 0:
        print("✅ No past due members found - nothing to process!")
        return
    
    # Show past due member summary
    print("\\n📊 PAST DUE MEMBERS SUMMARY:")
    print("-" * 40)
    for idx, row in past_due_df.iterrows():
        name = row.get('firstName', 'Unknown') + ' ' + row.get('lastName', '')
        amount = float(row.get('agreement_amountPastDue', 0))
        print(f"   • {name}: ${amount:.2f}")
    
    # Note: Square will handle invoice delivery automatically
    print("\\n📧 Square will handle invoice delivery to customers")
    
    # Process each past due member
    print(f"\\n📧 PROCESSING {len(past_due_df)} PAST DUE MEMBERS...")
    print("=" * 60)
    
    processed_count = 0
    skipped_count = 0
    invoice_created_count = 0
    error_count = 0
    
    for idx, row in past_due_df.iterrows():
        member_id = row['id']
        name = f"{row.get('firstName', '')} {row.get('lastName', '')}".strip()
        email = row.get('email', None)
        phone = row.get('mobilePhone', None)
        
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
        amount_due = float(row['agreement_amountPastDue'])
        recurring = row['agreement_recurringCost_parsed']
        
        if pd.isna(recurring) or recurring == 0:
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
        
        # Generate Square invoice
        print(f"   🧾 Creating Square invoice...")
        try:
            invoice_url = create_square_invoice(
                name, 
                amount_due, 
                description=breakdown,
                email=email
            )
            
            if not invoice_url:
                print(f"   ❌ Failed to create invoice (no URL returned)")
                df.at[idx, 'invoice_status'] = 'failed_invoice_creation'
                df.at[idx, 'invoice_error'] = 'No invoice URL returned'
                df.at[idx, 'processed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                error_count += 1
                processed_count += 1
                continue
            
            print(f"   ✅ Invoice created: {invoice_url}")
            df.at[idx, 'invoice_url'] = invoice_url
            df.at[idx, 'invoice_status'] = 'invoice_created_successfully'
            df.at[idx, 'processed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            invoice_created_count += 1
            
        except Exception as e:
            print(f"   ❌ Error creating invoice: {e}")
            df.at[idx, 'invoice_status'] = 'failed_invoice_creation'
            df.at[idx, 'invoice_error'] = str(e)
            df.at[idx, 'processed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_count += 1
            processed_count += 1
            continue
        
        # Square handles invoice delivery automatically
        print(f"   📧 Square will automatically send invoice to {email}")
        
        processed_count += 1
        
        # Be polite to APIs - small delay between requests
        time.sleep(2)
    
    # Save results to updated CSV
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
    print(f"❌ Errors encountered: {error_count}")
    
    success_rate = (invoice_created_count / len(past_due_df)) * 100 if past_due_df.size > 0 else 0
    print(f"📈 Success rate: {success_rate:.1f}%")
    
    print(f"\\n📄 Results saved to: {output_file}")
    print("✅ Past due invoice processing complete!")

if __name__ == "__main__":
    main()
