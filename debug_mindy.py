"""Debug both Mindy agreements."""
import sys
sys.path.insert(0, 'src')
from clubos_training_api_fixed import ClubOSTrainingPackageAPI
import time
import json

api = ClubOSTrainingPackageAPI()
api.authenticate()

# Mindy Feilbach
api.delegate_to_member('163020442')

# Both agreements
for agr_id in [1603572, 1605421]:
    print(f'\n==== AGREEMENT {agr_id} ====')
    timestamp = int(time.time() * 1000)
    
    url = f'https://anytime.club-os.com/api/agreements/package_agreements/V2/{agr_id}?include=invoices&include=scheduledPayments&include=prohibitChangeTypes&_={timestamp}'
    headers = {
        'Accept': '*/*',
        'Referer': 'https://anytime.club-os.com/action/PackageAgreementUpdated/spa/',
        'X-Requested-With': 'XMLHttpRequest'
    }
    resp = api.session.get(url, headers=headers, timeout=15)
    data = resp.json()
    
    pkg = data.get('data', {})
    print(f"Name: {pkg.get('name')}")
    print(f"Agreement Status: {pkg.get('agreementStatus')}")
    print(f"Start: {pkg.get('startDate')} Duration: {pkg.get('duration')} months")
    print(f"Billing: every {pkg.get('billingDuration')} weeks/months (type {pkg.get('billingDurationType')})")
    
    # Check member services for pricing
    services = pkg.get('packageAgreementMemberServices', [])
    for svc in services:
        unit_price = svc.get('unitPrice', 0)
        units = svc.get('unitsPerBillingDuration', 0)
        billing_total = float(unit_price) * float(units)
        print(f"  Service: {svc.get('name')} - ${unit_price} x {units} = ${billing_total} per billing cycle")
    
    include = data.get('include', {})
    invoices = include.get('invoices', [])
    scheduled = include.get('scheduledPayments', [])
    
    print(f'\nInvoices: {len(invoices)}')
    for inv in invoices:
        print(f"  - {inv.get('billingDate')} status={inv.get('invoiceStatus')} total=${inv.get('total')}")
    
    print(f'\nScheduled Payments: {len(scheduled)}')
    for sp in scheduled[:15]:
        print(f"  - {sp.get('scheduledDate')} status={sp.get('scheduledPaymentStatus')} total=${sp.get('total')}")
    
    # Calculate what SHOULD have been paid
    print('\n--- Billing Status Changes ---')
    changes = pkg.get('agreementBillingStatusChanges', [])
    for c in changes:
        print(f"  {c.get('eventDate')}: billingState={c.get('billingState')}")

print('\n\nDONE')
