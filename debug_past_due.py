"""Debug script to find the REAL past due amounts."""
import sys
sys.path.insert(0, 'src')
from clubos_training_api_fixed import ClubOSTrainingPackageAPI
import json

api = ClubOSTrainingPackageAPI()
api.authenticate()

# Get all assignees using the proper method
assignees = api.fetch_assignees()

# People we need to find based on user's verified list
target_names = [
    'Cecilia Gonzalez', 'Dale Roen', 'Diego Pastran', 'Javae Dixon',
    'Joe Benson', 'Kymberley Marr', 'Mary Siegmann', 'Michael Stephens',
    'Miguel Belmontes', 'Mindy Feilbach', 'Rashida Hull', 'Ziann Crump'
]

print(f"Total assignees: {len(assignees)}")
print()

# Find all target clients
targets_found = {}
for a in assignees:
    name = a.get('name', '')
    member_id = a.get('id', '')
    for t in target_names:
        if t.lower() in name.lower() or name.lower() in t.lower():
            targets_found[t] = a
            break

print(f"Found {len(targets_found)} target clients:")
for name, data in targets_found.items():
    print(f"  {name}: id={data.get('id')}")

print()

# Now check each one for their agreements and invoices
headers = {'Accept': 'application/json', 'Referer': 'https://anytime.club-os.com/action/ClubServicesNew'}

for name in ['Diego Pastran', 'Mindy Feilbach', 'Rashida Hull', 'Miguel Belmontes']:
    if name not in targets_found:
        print(f"\n=== {name} NOT FOUND ===")
        continue
    
    member_id = targets_found[name].get('id')
    print(f"\n{'='*60}")
    print(f"=== {name} (memberId={member_id}) ===")
    print('='*60)
    
    # Delegate to this member
    api.delegate_to_member(str(member_id))
    
    # Get package agreements list
    url = 'https://anytime.club-os.com/api/agreements/package_agreements/list'
    resp = api.session.get(url, headers=headers, timeout=15)
    
    if resp.status_code != 200:
        print(f"  ERROR: {resp.status_code}")
        continue
    
    data = resp.json()
    print(f"Found {len(data)} package agreements")
    
    total_past_due = 0
    
    for i, agr in enumerate(data):
        pkg = agr.get('packageAgreement', {})
        billing = agr.get('billingStatuses', {})
        agr_id = pkg.get('id')
        agr_status = pkg.get('agreementStatus')
        
        print(f"\n  Agreement {i+1}: ID={agr_id}")
        print(f"    Name: {pkg.get('name')}")
        print(f"    Agreement Status: {agr_status}")
        print(f"    Start: {pkg.get('startDate')} Duration: {pkg.get('duration')}")
        print(f"    Current billing: {billing.get('current')}")
        print(f"    Past billing events: {billing.get('past')}")
        
        # Get invoices
        if agr_id:
            invoice_url = f'https://anytime.club-os.com/api/agreements/package_agreements/{agr_id}/invoices'
            inv_resp = api.session.get(invoice_url, headers=headers, timeout=15)
            if inv_resp.status_code == 200:
                invoices = inv_resp.json()
                print(f"    Invoices: {len(invoices)} total")
                
                past_due = 0
                for inv in invoices:
                    status = inv.get('invoiceStatus')
                    amount = float(inv.get('invoiceTotal', 0))
                    date = inv.get('invoiceDate')
                    
                    # Status 1=paid, 2=pending, 3=rejected, 4=scheduled, 5=delinquent, 6=processing, 7=waiting, 8=chargeback
                    # Past due = 3, 5, 8
                    if status in [3, 5, 8]:
                        past_due += amount
                        total_past_due += amount
                        print(f"      ❌ PAST DUE: {date} status={status} amount=${amount}")
                    elif status in [2]:
                        print(f"      ⏳ PENDING: {date} status={status} amount=${amount}")
                    elif status in [4]:
                        print(f"      📅 SCHEDULED: {date} status={status} amount=${amount}")
                    elif status == 1:
                        pass  # paid, skip
                    else:
                        print(f"      ?: {date} status={status} amount=${amount}")
                
                if past_due > 0:
                    print(f"    Agreement past due: ${past_due}")
    
    print(f"\n  TOTAL PAST DUE FOR {name}: ${total_past_due}")

print("\n" + "="*60)
print("DONE")
