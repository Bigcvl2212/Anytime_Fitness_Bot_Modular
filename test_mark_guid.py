#!/usr/bin/env python3

import sys
sys.path.append('src')

from clubos_training_api_fixed import ClubOSTrainingPackageAPI
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.clubos_credentials_clean import CLUBOS_CREDENTIALS

# Test with Mark Benzinger's GUID
mark_guid = '66082049'
print(f'🧪 Testing with Mark Benzinger GUID: {mark_guid}')

api = ClubOSTrainingPackageAPI()
api.username = CLUBOS_USERNAME
api.password = CLUBOS_PASSWORD

print('🔐 Authenticating...')
if api.authenticate():
    print('✅ Authentication successful')
    print(f'🔐 Session cookies: {list(api.session.cookies.keys())}')
    
    print(f'👤 Delegating to GUID: {mark_guid}')
    if api.delegate_to_member(mark_guid):
        print('✅ Delegation successful')
        
        print('📋 Getting agreement IDs...')
        agreement_ids = api.discover_member_agreement_ids(mark_guid)
        print(f'🎯 RESULT: {len(agreement_ids)} agreement IDs found: {agreement_ids}')
        
        if agreement_ids:
            print('✅ SUCCESS: Agreement IDs found!')
        else:
            print('❌ FAIL: No agreement IDs found')
    else:
        print('❌ Delegation failed')
else:
    print('❌ Authentication failed')
