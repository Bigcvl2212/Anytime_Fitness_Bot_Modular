# Agreement Columns Migration for Collections System

## 🎯 Objective
Add agreement ID, GUID, and type columns to the members table to support the collections management system with complete agreement data.

## 📋 Changes Made

### 1. Database Schema Updates
- **SQLite (Local)**: ✅ Added `agreement_id`, `agreement_guid`, `agreement_type` columns
- **PostgreSQL (Production)**: ⏳ Ready to run migration script

### 2. Code Updates
- **Startup Sync**: ✅ Updated to extract and save agreement data from ClubHub API
- **Database Manager**: ✅ Updated INSERT statements to include agreement columns
- **Collections API**: ✅ Updated to use agreement data when available

## 🚀 Production Deployment Steps

### Step 1: Run PostgreSQL Migration
```bash
python add_agreement_columns_postgresql.py
```

### Step 2: Deploy Code Changes
The following files have been updated and need to be deployed:
- `src/services/multi_club_startup_sync.py` - Extract agreement data
- `src/services/database_manager.py` - Save agreement data
- `src/routes/members.py` - Use agreement data in collections

### Step 3: Trigger Data Sync
After deployment, run a full sync to populate the new agreement columns:
```bash
# This will fetch agreement data from ClubHub API and save to database
python -c "from src.services.multi_club_startup_sync import sync_all_clubs; sync_all_clubs()"
```

## 📊 Expected Results

### Before Migration
- Members in collections: No agreement IDs
- Training clients: Full agreement data ✅

### After Migration
- Members in collections: Full agreement data ✅
- Training clients: Full agreement data ✅

## 🔍 Verification

### Check Agreement Data
```sql
-- PostgreSQL
SELECT 
    full_name, 
    agreement_id, 
    agreement_type, 
    amount_past_due 
FROM members 
WHERE status_message LIKE '%Past Due%' 
LIMIT 5;
```

### Test Collections API
```bash
# Test the collections endpoint
curl http://localhost:5000/api/collections/past-due
```

## 📧 Collections Email Example

**Before (Members without agreement IDs):**
```
1. CHRIS BENNETT
   Amount Past Due: $276.43
   Type: Member
   Agreement ID: None
   Agreement Type: Membership
```

**After (Members with agreement IDs):**
```
1. CHRIS BENNETT
   Amount Past Due: $276.43
   Type: Member
   Agreement ID: 89636529
   Agreement Type: 0
```

## ⚠️ Important Notes

1. **Backward Compatibility**: Code handles both SQLite (no agreement columns) and PostgreSQL (with agreement columns)
2. **Data Source**: Agreement data comes from ClubHub API `/api/members/{id}/agreement` endpoint
3. **Sync Required**: New agreement columns will be empty until next full sync runs
4. **Gmail Setup**: Still need to set up App Password for email sending

## 🎉 Benefits

- **Complete Agreement Data**: Both members and training clients will have agreement IDs
- **Professional Collections**: Email will include all agreement details
- **Accurate Billing**: Agreement data matches what's in ClubHub system
- **Future-Proof**: Database schema supports all agreement information
