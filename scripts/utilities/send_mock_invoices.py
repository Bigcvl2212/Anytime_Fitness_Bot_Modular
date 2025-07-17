import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math

CONTACT_LIST_CSV = "master_contact_list_20250715_181714.csv"
CONTACT_LIST_XLSX = "master_contact_list_20250715_181714.xlsx"
LATE_FEE = 19.50
WAIVER_LOOKBACK_DAYS = 365

# Helper to check if a waiver is within the last year
def waiver_recent(waived_date):
    if pd.isna(waived_date) or not waived_date:
        return False
    try:
        waived_dt = pd.to_datetime(waived_date)
        return (datetime.now() - waived_dt).days < WAIVER_LOOKBACK_DAYS
    except Exception:
        return False

def main():
    df = pd.read_excel(CONTACT_LIST_XLSX, dtype=str)
    # Ensure numeric columns are float
    df['agreement.amountPastDue'] = pd.to_numeric(df['agreement.amountPastDue'], errors='coerce').fillna(0)
    df['agreement.recurringCost.total'] = pd.to_numeric(df['agreement.recurringCost.total'], errors='coerce').replace(0, np.nan)
    # Add columns if missing
    if 'late_fee_waived' not in df.columns:
        df['late_fee_waived'] = ''
    df['mock_invoice_message'] = ''
    df['mock_invoice_late_fees'] = 0.0
    df['mock_invoice_missed_payments'] = 0
    today_str = datetime.now().strftime('%Y-%m-%d')
    for idx, row in df.iterrows():
        amount_due = row['agreement.amountPastDue']
        recurring = row['agreement.recurringCost.total']
        name = row.get('Name') or f"{row.get('FirstName','')} {row.get('LastName','')}"
        waiver_date = row.get('late_fee_waived', '')
        # Only process if past due and recurring > 0
        if amount_due > 0 and not np.isnan(recurring):
            missed_payments = int(math.floor(amount_due / recurring))
            late_fees = missed_payments * LATE_FEE
            note = ''
            waived = False
            # Waiver logic
            if missed_payments >= 2 and not waiver_recent(waiver_date):
                note = ("You must respond within 7 days or your account will be sent to collections. "
                        "If you pay today in full, we can offer a one-time late fee waiver.")
                df.at[idx, 'late_fee_waived'] = today_str
                waived = True
            elif waiver_recent(waiver_date):
                note = "You have already received a late fee waiver in the past year."
            # Invoice message
            invoice = (f"Dear {name},\n\n"
                       f"Your account is past due. Amount owed: ${amount_due:.2f}. "
                       f"You have missed {missed_payments} biweekly payment(s). "
                       f"Late fees applied: ${late_fees:.2f}.\n"
                       f"Next payment due: {row.get('agreement.dateOfNextPayment','N/A')}\n"
                       f"Total remaining on contract: ${row.get('agreement.valueRemaining','N/A')}\n"
                       f"Regular payment: ${recurring:.2f}.\n"
                       f"{note}\n\n"
                       f"If you have questions, please contact us immediately.")
            df.at[idx, 'mock_invoice_message'] = invoice
            df.at[idx, 'mock_invoice_late_fees'] = late_fees
            df.at[idx, 'mock_invoice_missed_payments'] = missed_payments
        else:
            # Not past due or no recurring cost
            df.at[idx, 'mock_invoice_message'] = ''
            df.at[idx, 'mock_invoice_late_fees'] = 0.0
            df.at[idx, 'mock_invoice_missed_payments'] = 0
    # Save
    df.to_excel(CONTACT_LIST_XLSX, index=False)
    df.to_csv(CONTACT_LIST_CSV, index=False)
    print("Mock invoices generated and saved to master contact list.")

if __name__ == "__main__":
    main() 