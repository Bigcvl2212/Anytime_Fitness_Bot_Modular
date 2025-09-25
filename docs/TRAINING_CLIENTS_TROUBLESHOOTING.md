# Training Clients Invoice Data - Troubleshooting Checklist

## 🚨 Quick Diagnosis Steps

When training client invoice data is not working properly, follow this checklist:

### 1. Authentication Issues ✅
- [ ] Check if ClubOS credentials exist in SecureSecretsManager
  ```bash
  # Verify credentials
  python -c "from src.services.authentication.secure_secrets_manager import SecureSecretsManager; sm = SecureSecretsManager(); print('Username:', bool(sm.get_secret('clubos-username'))); print('Password:', bool(sm.get_secret('clubos-password')))"
  ```
- [ ] Test manual ClubOS login at https://anytime.club-os.com/action/SignIn
- [ ] Check for JSESSIONID and apiV3AccessToken cookies in session
- [ ] Verify unified_auth_service.authenticate_clubos() returns authenticated session

### 2. Assignees Discovery Issues ✅
- [ ] Test assignees endpoint directly:
  ```python
  training_api = ClubOSTrainingPackageAPI()
  training_api.authenticate()
  assignees = training_api.fetch_assignees()
  print(f"Found {len(assignees)} assignees")
  ```
- [ ] Check /action/Assignees page loads in browser
- [ ] Verify HTML parsing finds delegate(MEMBER_ID) patterns
- [ ] Check AJAX endpoint: `/action/Assignees/members?_=timestamp`

### 3. Agreement Discovery Issues ✅
- [ ] Test with known training client ID:
  ```python
  member_id = "191015549"  # Known training client
  agreements = training_api.discover_member_agreement_ids(member_id)
  print(f"Found agreement IDs: {agreements}")
  ```
- [ ] Check delegation working: `/action/Delegate/{member_id}/url=false`
- [ ] Verify SPA context: `/action/PackageAgreementUpdated/spa/`
- [ ] Test API endpoint: `/api/agreements/package_agreements/list?memberId={id}`

### 4. Invoice Data Issues ✅
- [ ] Test billing status for known agreement:
  ```python
  agreement_id = "1616463"  # Known agreement
  billing_data = training_api.get_complete_agreement_data(agreement_id)
  print(f"Billing status: {billing_data}")
  ```
- [ ] Check all invoice endpoints return data:
  - `/api/agreements/package_agreements/{id}/billing_status`
  - `/api/agreements/package_agreements/V2/{id}?include=invoices`
  - `/api/agreements/package_agreements/{id}/salespeople`
- [ ] Verify amount calculation logic processes all fields

### 5. Database Issues ✅
- [ ] Check training_clients table exists:
  ```sql
  SELECT COUNT(*) FROM training_clients;
  SELECT * FROM training_clients WHERE payment_status = 'Past Due' LIMIT 5;
  ```
- [ ] Verify JSON fields are properly serialized
- [ ] Check database connection (SQLite vs PostgreSQL)
- [ ] Ensure DatabaseManager.save_training_clients_to_db() returns True

## 🔍 Common Error Patterns & Solutions

### Error: "No assignees found from ClubOS"
**Cause**: Authentication failure or HTML parsing issue
**Solution**: 
1. Re-authenticate manually
2. Check /action/Assignees page structure hasn't changed
3. Update HTML parsing patterns if needed

### Error: "No agreement IDs found for member"
**Cause**: Missing delegation or incorrect API parameters
**Solution**:
1. Verify delegation_to_member() sets delegatedUserId cookie
2. Check API endpoint parameters match HAR files
3. Include proper referer headers and timestamps

### Error: "$0.00 past due for known past due client"
**Cause**: Billing data extraction failing
**Solution**:
1. Check all billing endpoints return valid data
2. Verify amount calculation processes all fields
3. Test against ClubOS dashboard manually

### Error: "Thread safety issues / session conflicts"
**Cause**: Concurrent access to shared session
**Solution**:
1. Use thread-local API instances
2. Create separate authenticated sessions per thread
3. Implement proper session cleanup

### Error: "Database save fails"
**Cause**: JSON serialization or schema mismatch
**Solution**:
1. Check complex fields are properly JSON serialized
2. Verify database schema matches expected structure
3. Test with simple data first, then add complexity

## 🧪 Test Scripts for Validation

### Test Authentication
```bash
python -c "
from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI
api = ClubOSTrainingPackageAPI()
result = api.authenticate()
print(f'Authentication: {result}')
print(f'Session cookies: {list(api.session.cookies.keys())}')
"
```

### Test Known Training Client
```bash
python -c "
from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI
api = ClubOSTrainingPackageAPI()
if api.authenticate():
    # Test with Dennis Radant (known past due client)
    agreements = api.get_member_package_agreements('191015549')
    print(f'Found {len(agreements)} agreements')
    for i, agreement in enumerate(agreements):
        print(f'  {i+1}. ID: {agreement.get(\"agreement_id\")}, Status: {agreement.get(\"payment_status\")}, Amount: \${agreement.get(\"amount_owed\", 0):.2f}')
"
```

### Test Database Operations
```bash
python -c "
from src.services.database_manager import DatabaseManager
db = DatabaseManager()
count = db.get_training_client_count()
print(f'Training clients in database: {count}')
past_due = db.execute_query('SELECT COUNT(*) as count FROM training_clients WHERE payment_status = \"Past Due\"', fetch_one=True)
print(f'Past due clients: {past_due[\"count\"] if past_due else 0}')
"
```

## 📊 Data Validation Checkpoints

### Financial Data Validation
Compare system amounts with ClubOS dashboard:
1. Login to ClubOS → Personal Training → Client name
2. Check "Billing" tab for past due amount
3. Compare with database: `SELECT past_due_amount FROM training_clients WHERE full_name = 'Client Name'`
4. Amounts should match exactly

### Agreement Status Validation
Verify only active agreements are processed:
1. Check ClubOS agreement status codes (2 = Active, 5 = Cancelled)
2. Ensure cancelled agreements don't contribute to past due amounts
3. Validate agreement filtering logic

### Client Discovery Validation
Ensure all training clients are found:
1. Count assignees in ClubOS Personal Training dashboard
2. Compare with system count: `SELECT COUNT(*) FROM training_clients`
3. Investigate discrepancies

## 🔧 Emergency Recovery Steps

If the entire invoice data system breaks:

1. **Backup Current State**
   ```bash
   # Backup database
   cp gym_bot.db gym_bot_backup_$(date +%Y%m%d_%H%M%S).db
   
   # Backup key files
   cp -r src/services/api src_services_api_backup_$(date +%Y%m%d_%H%M%S)
   ```

2. **Restore from Known Working State**
   ```bash
   # Restore from git if needed
   git checkout restore/2025-08-29-15-21
   git reset --hard 10cf65a  # September 19th working commit
   ```

3. **Test Core Components**
   - Test authentication first
   - Test assignees discovery
   - Test single client agreement retrieval
   - Test database operations

4. **Gradual Restoration**
   - Start with single client processing
   - Add parallel processing after core works
   - Validate each step before proceeding

## 📞 Support Contacts

- **System Owner**: Jeremy Mayo (j.mayo)
- **Codebase**: `/c/Users/mayoj/OneDrive/Documents/Gym-Bot/gym-bot/gym-bot-modular/`
- **Documentation**: `docs/TRAINING_CLIENTS_INVOICE_DATA_PROCESS.md`
- **Technical Flow**: `docs/TRAINING_CLIENTS_TECHNICAL_FLOW.md`

---

**Remember**: The training clients invoice data is critical for collections and revenue tracking. Always test thoroughly and maintain backups when making changes.