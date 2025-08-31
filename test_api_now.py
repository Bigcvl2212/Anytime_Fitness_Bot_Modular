import requests

try:
    response = requests.get('http://localhost:5000/api/members/past-due')
    data = response.json()
    
    members = data.get('members', [])
    print(f'API returning {len(members)} past due members')
    
    if members:
        print('\nFirst 5 members from API:')
        for m in members[:5]:
            name = m.get('full_name', 'Unknown')
            total = m.get('amount_past_due', 0)
            base = m.get('base_amount_past_due', 0)
            missed = m.get('missed_payments', 0)
            fees = m.get('late_fees', 0)
            print(f'  {name}: Total=${total:.2f}, Base=${base:.2f}, Missed={missed}, Fees=${fees:.2f}')
    else:
        print('No members returned by API')
        
except Exception as e:
    print(f'Error: {e}')
