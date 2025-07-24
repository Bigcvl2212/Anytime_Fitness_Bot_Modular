import pandas as pd
import numpy as np
import math

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

def should_exclude_member(name):
    """Check if member should be excluded (Connor Ratzke - already paid)"""
    name_lower = str(name).lower()
    return 'connor' in name_lower and 'ratzke' in name_lower

# Load data
df = pd.read_csv('master_contact_list_with_agreements_20250722_180712.csv', dtype=str)
df['agreement_amountPastDue'] = pd.to_numeric(df['agreement_amountPastDue'], errors='coerce').fillna(0)

print('=== DIAGNOSTIC ===')
total_past_due = len(df[df['agreement_amountPastDue'] > 0])
print(f'Total past due members: {total_past_due}')

valid_count = 0
for idx, row in df.iterrows():
    amount_due = float(row.get('agreement_amountPastDue', 0))
    if amount_due <= 0:
        continue
        
    name = row.get('Name') or f"{row.get('FirstName','')} {row.get('LastName','')}"
    name = name.strip()
    if not name:
        print(f"[SKIP] Row {idx}: No name - Name='{row.get('Name')}' FirstName='{row.get('FirstName')}' LastName='{row.get('LastName')}'")
        continue
    
    if should_exclude_member(name):
        print(f"[SKIP] {name}: Excluded (Connor Ratzke)")
        continue
        
    email = row.get('Email') or row.get('email')
    if not email or not isinstance(email, str) or '@' not in email:
        print(f"[SKIP] {name}: No email - Email='{email}'")
        continue
        
    recurring = parse_recurring_cost(row.get('agreement_recurringCost'))
    if recurring == 0:
        print(f"[SKIP] {name}: No recurring cost - Raw='{row.get('agreement_recurringCost')}'")
        continue
    
    valid_count += 1
    if valid_count <= 5:  # Show first 5
        print(f"[VALID] {name}: ${amount_due} due, ${recurring} recurring, email={email}")

print(f"\nValid members found: {valid_count}")
