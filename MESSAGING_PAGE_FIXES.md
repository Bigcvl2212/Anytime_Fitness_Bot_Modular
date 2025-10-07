# Messaging Page Issues & Fixes

## Issues Found

### 1. Category Counts Not Loading
**Problem**: The messaging page JavaScript calls `loadStatusCampaigns()` which tries to fetch data from:
- `/api/prospects/all` 
- `/api/members/all` (works)
- `/api/training/clients` (may not exist or returns wrong format)

**Root Cause**: The prospects and training endpoints either don't exist or return data in unexpected formats.

**Location**: `templates/messaging.html` line 1707-1857

### 2. Past Campaigns Not Loading  
**Problem**: The `loadCampaignHistory()` function calls `/api/campaigns/history` but may be getting authentication errors or returning empty data.

**Location**: `templates/messaging.html` line 3048-3150

## Required Fixes

### Fix 1: Add Missing Prospects Endpoint
The messaging page needs `/api/prospects/all` endpoint that doesn't exist. We need to add this to either `members.py` or create a new `prospects.py` route file.

```python
@members_bp.route('/api/prospects/all')
def get_all_prospects():
    """Get all prospects from database"""
    try:
        query = """
            SELECT
                prospect_id,
                id,
                first_name,
                last_name,
                full_name,
                email,
                phone as mobile_phone,
                status
            FROM prospects
            ORDER BY full_name
        """
        
        result = current_app.db_manager.execute_query(query, fetch_all=True)
        prospects = [dict(row) for row in result] if result else []
        
        logger.info(f"✅ Retrieved {len(prospects)} prospects from database")
        return jsonify({'success': True, 'prospects': prospects})
        
    except Exception as e:
        logger.error(f"❌ Error getting prospects: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

### Fix 2: Add Missing Training Clients Endpoint
The messaging page needs `/api/training/clients` endpoint.

```python
@members_bp.route('/api/training/clients')
def get_all_training_clients():
    """Get all training clients from database"""
    try:
        query = """
            SELECT
                clubos_member_id,
                member_name as full_name,
                email,
                phone as mobile_phone,
                payment_status,
                total_past_due as past_due_amount,
                status_message
            FROM training_clients
            ORDER BY member_name
        """
        
        result = current_app.db_manager.execute_query(query, fetch_all=True)
        training_clients = [dict(row) for row in result] if result else []
        
        logger.info(f"✅ Retrieved {len(training_clients)} training clients from database")
        return jsonify({'success': True, 'training_clients': training_clients})
        
    except Exception as e:
        logger.error(f"❌ Error getting training clients: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

### Fix 3: Verify Campaign History Endpoint
The endpoint exists in `messaging.py` line 1066, but may not be returning data properly. Check if the `campaigns` table exists and has data.

```python
@messaging_bp.route('/api/campaigns/history', methods=['GET'])
def get_campaign_history():
    """Get campaign history"""
    try:
        limit = int(request.args.get('limit', 20))
        
        # Ensure campaigns table exists
        current_app.db_manager.execute_query('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY,
                campaign_name TEXT,
                message_text TEXT,
                message_type TEXT,
                subject TEXT,
                categories TEXT,
                total_recipients INTEGER,
                successful_sends INTEGER,
                failed_sends INTEGER,
                errors TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        campaigns = current_app.db_manager.execute_query('''
            SELECT * FROM campaigns 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,), fetch_all=True)
        
        if not campaigns:
            campaigns = []
        
        # Convert to list of dicts
        campaigns_list = [dict(row) for row in campaigns] if campaigns else []
        
        return jsonify({'success': True, 'campaigns': campaigns_list})
        
    except Exception as e:
        logger.error(f"❌ Error getting campaign history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

## Implementation Steps

1. **Add Prospects Endpoint** - Add to `src/routes/members.py`
2. **Add Training Clients Endpoint** - Add to `src/routes/members.py`
3. **Verify Campaigns Table** - Check if table exists and create if needed
4. **Test Endpoints** - Visit each endpoint in browser to verify they return data:
   - http://localhost:5000/api/prospects/all
   - http://localhost:5000/api/training/clients
   - http://localhost:5000/api/campaigns/history

## Testing

After implementing fixes, test the messaging page:
1. Navigate to `/messaging`
2. Check browser console for errors
3. Verify category badges show counts
4. Verify past campaigns section loads (or shows "No campaigns yet")
5. Try sending a test campaign to verify the full flow works

## Expected Behavior After Fixes

- **Category Counts**: All badges should show numbers (e.g., "Good Standing: 296", "Past Due 6-30: 15")
- **Past Campaigns**: Either show list of previous campaigns OR show "No campaign history yet" message
- **No Console Errors**: Browser console should not show 404 errors for the API endpoints
