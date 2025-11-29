"""Debug V2 invoice endpoint for Mindy."""
import sys
sys.path.insert(0, 'src')
from clubos_training_api_fixed import ClubOSTrainingPackageAPI
import time
import json

api = ClubOSTrainingPackageAPI()
api.authenticate()

# Mindy Feilbach - delinquent
api.delegate_to_member('163020442')

# Agreement 1603572 (delinquent)
agr_id = 1603572
timestamp = int(time.time() * 1000)

url = f'https://anytime.club-os.com/api/agreements/package_agreements/V2/{agr_id}?include=invoices&include=scheduledPayments&include=prohibitChangeTypes&_={timestamp}'
headers = {
    'Accept': '*/*',
    'Referer': 'https://anytime.club-os.com/action/PackageAgreementUpdated/spa/',
    'X-Requested-With': 'XMLHttpRequest'
}
resp = api.session.get(url, headers=headers, timeout=15)
data = resp.json()

print('=== TOP LEVEL KEYS ===')
print(list(data.keys()))
print()
print('=== INCLUDE ===')
include = data.get('include', {})
print('Include keys:', list(include.keys()) if isinstance(include, dict) else type(include))
print()

if 'invoices' in include:
    invoices = include['invoices']
    print(f'=== INVOICES ({len(invoices)}) ===')
    past_due = 0
    for inv in invoices:
        status = inv.get('invoiceStatus')
        amount = float(inv.get('invoiceTotal', 0))
        date = inv.get('invoiceDate')
        print(f'  Invoice: {date} status={status} amount=${amount}')
        if status in [3, 5, 8]:
            past_due += amount
    print(f'TOTAL PAST DUE (status 3,5,8): ${past_due}')
    print()
    
    # Print full invoice detail for first one
    if invoices:
        print('=== FULL INVOICE DETAIL ===')
        print(json.dumps(invoices[0], indent=2))
if 'scheduledPayments' in include:
    sched = include['scheduledPayments']
    print(f'=== SCHEDULED PAYMENTS ({len(sched)}) ===')
    for sp in sched[:10]:
        print(f'  - {sp.get("scheduledDate")} status={sp.get("scheduledPaymentStatus")} amount=${sp.get("total")}')

# Print full data structure
print('=== DATA ===')
print(json.dumps(data.get('data', {}), indent=2)[:3000])
