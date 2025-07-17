import pandas as pd
import numpy as np
from datetime import datetime
import math
import time
from services.payments.square_client_fixed import create_square_invoice
from send_invoice_via_clubos import login_and_get_session, send_invoice_via_clubos

CONTACT_LIST_XLSX = "master_contact_list_20250715_181714.xlsx"
CONTACT_LIST_CSV = "master_contact_list_20250715_181714.csv"
LATE_FEE = 19.50

# Helper to determine if a member is past due (yellow/red)
def is_past_due(row):
    try:
        amt_due = float(row.get('agreement.amountPastDue', 0))
        return amt_due > 0
    except Exception:
        return False

def main():
    df = pd.read_excel(CONTACT_LIST_XLSX, dtype=str)
    df['agreement.amountPastDue'] = pd.to_numeric(df['agreement.amountPastDue'], errors='coerce').fillna(0)
    df['agreement.recurringCost.total'] = pd.to_numeric(df['agreement.recurringCost.total'], errors='coerce').replace(0, np.nan)
    df['mock_invoice_status'] = ''
    df['mock_invoice_url'] = ''
    df['mock_invoice_error'] = ''
    session = login_and_get_session()
    if not session:
        print("❌ Cannot proceed without ClubOS login.")
        return
    for idx, row in df.iterrows():
        if not is_past_due(row):
            continue
        member_id = row['ProspectID']
        name = row.get('Name') or f"{row.get('FirstName','')} {row.get('LastName','')}"
        email = row.get('Email', None)
        phone = row.get('Phone', None)
        if not email or not isinstance(email, str) or '@' not in email:
            print(f"[SKIP] {name}: No valid email, cannot send invoice.")
            df.at[idx, 'mock_invoice_status'] = 'skipped_no_email'
            continue
        amount_due = float(row['agreement.amountPastDue'])
        recurring = row['agreement.recurringCost.total']
        if np.isnan(recurring) or recurring == 0:
            df.at[idx, 'mock_invoice_status'] = 'Skipped: No recurring cost'
            continue
        missed_payments = int(math.floor(amount_due / recurring))
        late_fees = missed_payments * LATE_FEE
        # Invoice breakdown
        breakdown = (f"Overdue Payment - {missed_payments} missed payments, "
                     f"{missed_payments} late fees ($19.50 each) included. "
                     "YOU MUST RESPOND TO THIS MESSAGE OR PAY THIS INVOICE IN FULL WITHIN 7 DAYS OR YOUR ACCOUNT WILL BE FLAGGED FOR COLLECTIONS.")
        # Generate Square invoice
        try:
            invoice_url = create_square_invoice(name, amount_due, description=breakdown, email=email, phone=phone)
            if not invoice_url:
                df.at[idx, 'mock_invoice_status'] = 'Failed to create invoice'
                df.at[idx, 'mock_invoice_error'] = 'No invoice URL returned'
                continue
        except Exception as e:
            df.at[idx, 'mock_invoice_status'] = 'Failed to create invoice'
            df.at[idx, 'mock_invoice_error'] = str(e)
            continue
        # Compose ClubOS message/email
        message = (f"Dear {name},\n\n"
                   f"Your account is past due. Amount owed: ${amount_due:.2f}. "
                   f"You have missed {missed_payments} biweekly payment(s). "
                   f"Late fees applied: ${late_fees:.2f}.\n"
                   f"Next payment due: {row.get('agreement.dateOfNextPayment','N/A')}\n"
                   f"Total remaining on contract: ${row.get('agreement.valueRemaining','N/A')}\n"
                   f"Regular payment: ${recurring:.2f}.\n"
                   f"Invoice link: {invoice_url}\n\n"
                   "YOU MUST RESPOND TO THIS MESSAGE OR PAY THIS INVOICE IN FULL WITHIN 7 DAYS OR YOUR ACCOUNT WILL BE FLAGGED FOR COLLECTIONS.")
        # Send via ClubOS (email and SMS)
        try:
            success = send_invoice_via_clubos(
                session,
                amount=amount_due,
                description=breakdown,
                payment_url=invoice_url,
                recipient_name=name,
                recipient_email=email,
                recipient_phone=phone,
                extra_message=message
            )
            if success:
                df.at[idx, 'mock_invoice_status'] = 'Sent'
                df.at[idx, 'mock_invoice_url'] = invoice_url
            else:
                df.at[idx, 'mock_invoice_status'] = 'Failed to send message'
                df.at[idx, 'mock_invoice_error'] = 'ClubOS send failed'
        except Exception as e:
            df.at[idx, 'mock_invoice_status'] = 'Failed to send message'
            df.at[idx, 'mock_invoice_error'] = str(e)
        # Be polite to APIs
        time.sleep(1)
    # Save results
    df.to_excel(CONTACT_LIST_XLSX, index=False)
    df.to_csv(CONTACT_LIST_CSV, index=False)
    print("Live invoices and messages sent. Results saved to master contact list.")

if __name__ == "__main__":
    main() 