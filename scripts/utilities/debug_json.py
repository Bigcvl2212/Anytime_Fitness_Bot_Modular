import pandas as pd
import json

# Load the master contact list
df = pd.read_excel('master_contact_list_20250715_183530.xlsx')

# Get the first 10 members
members = df[df['Category'] == 'Member'].head(10)

print("=== RAW JSON FOR FIRST 10 MEMBERS ===")
for i, row in members.iterrows():
    print(f"\n--- MEMBER {i+1}: {row['Name']} ---")
    try:
        raw_data = json.loads(row['RawData'])
        print(json.dumps(raw_data, indent=2))
    except:
        print("No RawData available")
    print("-" * 50)

print("\n=== CHECKING FOR PAST DUE FIELDS ===")
for i, row in members.iterrows():
    print(f"\nMember: {row['Name']}")
    print(f"PastDue: {row['PastDue']}")
    print(f"PastDueDays: {row['PastDueDays']}")
    print(f"Status: {row['Status']}")
    print(f"StatusMessage: {row['StatusMessage']}") 