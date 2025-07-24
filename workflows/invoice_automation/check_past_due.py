import pandas as pd

df = pd.read_csv('master_contact_list_with_agreements_20250722_180712.csv', dtype=str)
df['agreement_amountPastDue'] = pd.to_numeric(df['agreement_amountPastDue'], errors='coerce').fillna(0)

past_due = df[df['agreement_amountPastDue'] > 0]
print(f'Past due members: {len(past_due)}')

has_email = past_due[past_due['email'].notna() & (past_due['email'] != '') & past_due['email'].str.contains('@', na=False)]
print(f'Past due with email: {len(has_email)}')

print('\nSample past due members:')
for i, row in past_due.head(10).iterrows():
    name = f"{row.get('firstName', '')} {row.get('lastName', '')}".strip()
    email = row.get('email', 'NO EMAIL')
    amount = row['agreement_amountPastDue']
    print(f'  {name} - ${amount} - {email}')
