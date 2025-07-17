import pandas as pd

# Load the master contact list
df = pd.read_excel('master_contact_list_20250715_181714.xlsx')

print("=== MASTER CONTACT LIST ANALYSIS ===")
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print("\nAll columns:")
for i, col in enumerate(df.columns):
    print(f"{i+1:2d}. {col}")

print("\n=== TRAINING-RELATED COLUMNS ===")
training_cols = [col for col in df.columns if 'training' in col.lower()]
print(f"Found {len(training_cols)} training-related columns:")
for col in training_cols:
    print(f"  - {col}")

print("\n=== SAMPLE OF TRAINING DATA ===")
if training_cols:
    print(df[training_cols].head())
else:
    print("No training columns found!")

print("\n=== CHECKING FOR TRAINING CLIENTS ===")
# Look for rows with training data
has_training_data = df.apply(lambda row: any([
    pd.notna(row.get('Member Name_training', pd.NA)),
    pd.notna(row.get('Agreement Name_training', pd.NA)),
    pd.notna(row.get('Next Invoice Subtotal_training', pd.NA))
]), axis=1)

training_clients = df[has_training_data]
print(f"Found {len(training_clients)} rows with training data")

if len(training_clients) > 0:
    print("\nSample training clients:")
    sample_cols = ['Name', 'ProspectID', 'Member Name_training', 'Agreement Name_training', 'Next Invoice Subtotal_training']
    available_cols = [col for col in sample_cols if col in df.columns]
    print(training_clients[available_cols].head()) 