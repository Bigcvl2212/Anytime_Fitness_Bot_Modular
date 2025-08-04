import pandas as pd

# Read the CSV file
df = pd.read_csv('data/exports/master_contact_list_20250715_181954.csv')

if 'StatusMessage' in df.columns:
    print('=== EXACT MATCHES ===')
    past_due_30_plus = df[df['StatusMessage'] == 'Past Due more than 30 days.']
    past_due_6_30 = df[df['StatusMessage'] == 'Past Due 6-30 days']
    print(f'Exact "Past Due more than 30 days.": {len(past_due_30_plus)}')
    print(f'Exact "Past Due 6-30 days": {len(past_due_6_30)}')
    
    print('\n=== ALL PAST DUE VARIATIONS ===')
    all_past_due = df[df['StatusMessage'].str.contains('Past Due|past due', case=False, na=False)]
    for status, count in all_past_due['StatusMessage'].value_counts().items():
        print(f'{count:3d}: "{status}"')
        
    print('\n=== CHECKING FOR SIMILAR PATTERNS ===')
    # Check for any other patterns that might be past due
    six_thirty = df[df['StatusMessage'].str.contains('6.*30|30.*day|6-30', case=False, na=False)]
    for status, count in six_thirty['StatusMessage'].value_counts().items():
        print(f'6-30 pattern {count:3d}: "{status}"')
        
    print('\n=== CHECKING FOR PUNCTUATION VARIATIONS ===')
    # Check for variations with different punctuation
    past_due_variations = df[df['StatusMessage'].str.contains('Past Due.*6.*30', case=False, na=False)]
    for status, count in past_due_variations['StatusMessage'].value_counts().items():
        print(f'6-30 variation {count:3d}: "{status}"')
        
    print('\n=== ALL STATUS MESSAGES (TOP 15) ===')
    for status, count in df['StatusMessage'].value_counts().head(15).items():
        print(f'{count:3d}: "{status}"')
        
    print('\n=== MEMBERS WHO MIGHT BE PAST DUE ===')
    # Look for other patterns that might indicate past due status
    potentially_past_due = df[df['StatusMessage'].str.contains('due|overdue|delinquent|behind|late|expire|cancel', case=False, na=False)]
    for status, count in potentially_past_due['StatusMessage'].value_counts().items():
        print(f'{count:3d}: "{status}"')
else:
    print('StatusMessage column not found')
