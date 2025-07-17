import pandas as pd

# Load the master contact list
df = pd.read_excel('master_contact_list_20250715_181714.xlsx')

print("=== TRAINING DATA COLUMNS ===")
# These are the columns from the QuickSight export that should be present
training_export_cols = ['ID', 'Member Name', 'Profile', 'Member Location', 'Agreement Location', 'Agreement Name', 'Next Invoice Subtotal']
existing_cols = [col for col in training_export_cols if col in df.columns]
print(f"Found {len(existing_cols)} training export columns:")
for col in existing_cols:
    print(f"  - {col}")

print("\n=== TRAINING CLIENTS ===")
# Look for rows that have training data (non-null values in training columns)
has_training_data = df[existing_cols].notna().any(axis=1)
training_clients = df[has_training_data]
print(f"Found {len(training_clients)} training clients")

if len(training_clients) > 0:
    print("\nSample training clients:")
    print(training_clients[existing_cols].head(10))
    
    print("\n=== AGREEMENT TYPES ===")
    if 'Agreement Name' in df.columns:
        agreement_types = df['Agreement Name'].value_counts()
        print("Agreement types found:")
        print(agreement_types)
else:
    print("No training clients found!") 