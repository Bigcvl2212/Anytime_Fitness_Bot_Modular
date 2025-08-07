#!/usr/bin/env python3
"""
Search CSV files for Dennis Rost
"""
import pandas as pd
import os

def search_csv_for_dennis():
    print('=== SEARCHING CSV FILES FOR DENNIS ROST ===')

    # Check master contact list
    csv_path = 'data/csv_exports/master_contact_list_with_agreements_20250802_123437.csv'
    if os.path.exists(csv_path):
        print(f'\n1. Checking: {csv_path}')
        try:
            df = pd.read_csv(csv_path)
            print(f'   📊 Total rows: {len(df)}')
            print(f'   📊 Columns: {list(df.columns)[:10]}...')  # Show first 10 columns
            
            # Search for Dennis or Rost in all text columns
            dennis_mask = df.astype(str).apply(lambda x: x.str.contains('Dennis|Rost', case=False, na=False)).any(axis=1)
            dennis_rows = df[dennis_mask]
            
            if not dennis_rows.empty:
                print(f'  ✅ Found {len(dennis_rows)} matching rows:')
                for idx, row in dennis_rows.iterrows():
                    first_name = row.get('firstName', 'N/A')
                    last_name = row.get('lastName', 'N/A') 
                    email = row.get('email', 'N/A')
                    member_id = row.get('id', 'N/A')
                    print(f'    - ID: {member_id}, Name: {first_name} {last_name}, Email: {email}')
            else:
                print('  ❌ No Dennis Rost found in master contact list')
                
        except Exception as e:
            print(f'  ❌ Error reading CSV: {e}')
    else:
        print('  ❌ Master contact list CSV not found')

    # Check training clients
    training_csv = 'data/csv_exports/Clients_1753310478191.csv'
    if os.path.exists(training_csv):
        print(f'\n2. Checking: {training_csv}')
        try:
            df_training = pd.read_csv(training_csv)
            print(f'   📊 Total rows: {len(df_training)}')
            print(f'   📊 Columns: {list(df_training.columns)}')
            
            # Search for Dennis or Rost in training clients
            dennis_mask = df_training.astype(str).apply(lambda x: x.str.contains('Dennis|Rost', case=False, na=False)).any(axis=1)
            dennis_training = df_training[dennis_mask]
            
            if not dennis_training.empty:
                print(f'  ✅ Found {len(dennis_training)} matching training clients:')
                for idx, row in dennis_training.iterrows():
                    client_id = row.get('ID', 'N/A')
                    member_name = row.get('Member Name', 'N/A')
                    trainers = row.get('Assigned Trainers', 'N/A')
                    print(f'    - ID: {client_id}, Name: {member_name}, Trainers: {trainers}')
            else:
                print('  ❌ No Dennis Rost found in training clients CSV')
                
        except Exception as e:
            print(f'  ❌ Error reading training CSV: {e}')
    else:
        print('  ❌ Training clients CSV not found')

    # Let's also check what names we DO have in training clients
    print(f'\n3. Sample training client names:')
    try:
        df_training = pd.read_csv('data/csv_exports/Clients_1753310478191.csv')
        sample_names = df_training['Member Name'].head(10).tolist()
        for name in sample_names:
            print(f'    - {name}')
    except Exception as e:
        print(f'  ❌ Error: {e}')

if __name__ == "__main__":
    search_csv_for_dennis()
