# Multi-Manager Setup Guide

## 🎯 Overview

Your gym bot now supports **multiple managers**, where each manager can enter their own credentials for their gym. This means Tyler can use his own Square account, ClubOS login, and ClubHub credentials without seeing yours.

---

## 📋 How It Works

### For You (First Manager)

1. **Initial Setup (.env file)**
   - Your credentials go in the `.env` file (for bootstrapping)
   - These are used as the default/fallback credentials

2. **Your Credentials Page**
   - After logging in, go to `/admin/credentials`
   - Enter all your API credentials
   - These are stored encrypted in the database linked to YOUR manager_id

### For Tyler (Second Manager)

1. **Gets His Own Login**
   - You create a login for him using the admin panel
   - He gets his own `manager_id`

2. **Enters His Own Credentials**
   - He logs in and goes to `/admin/credentials`
   - Enters HIS Square token, ClubOS login, ClubHub credentials
   - These are stored separately from yours

3. **Automatic Credential Switching**
   - When Tyler is logged in, the app uses HIS credentials
   - When you're logged in, the app uses YOUR credentials
   - **No mixing or conflicts!**

---

## 🔐 Security Features

### Credential Storage
- ✅ Encrypted in database
- ✅ Linked to individual manager_id
- ✅ Never shared between managers
- ✅ Only accessible when logged in

### Access Control
- ✅ Each manager only sees their own data
- ✅ Credentials are session-based
- ✅ Automatic logout after inactivity

---

## 🚀 Setup Instructions

### Step 1: Update Your .env File

Open `.env` and add your credentials (for initial setup):

```bash
# Your ClubOS Credentials
CLUBOS_USERNAME=your_actual_username
CLUBOS_PASSWORD=your_actual_password

# Your Square Credentials
SQUARE_PRODUCTION_ACCESS_TOKEN=your_actual_square_token
SQUARE_PRODUCTION_LOCATION_ID=your_actual_location_id

# Your ClubHub Credentials
CLUBHUB_EMAIL=your_actual_email
CLUBHUB_PASSWORD=your_actual_password
```

### Step 2: Start the App

```bash
python run_dashboard.py
```

### Step 3: Access Credentials Page

1. Log in to the admin panel
2. Navigate to: **`http://localhost:5000/admin/credentials`**
3. Fill in all your credentials
4. Click "Save Credentials"

### Step 4: Create Tyler's Account

1. Go to Admin Panel → User Management
2. Click "Add New Admin"
3. Enter Tyler's details:
   - Manager ID: `tyler_manager_id` (or similar)
   - Username: `tyler`
   - Email: tyler's email
4. Create the account

### Step 5: Tyler's First Login

1. Tyler logs in with his credentials
2. He goes to `/admin/credentials`
3. He enters HIS Square, ClubOS, and ClubHub credentials
4. Saves them

---

## 📊 How Credential Lookup Works

```
User logs in
    ↓
Session created with manager_id
    ↓
User makes API request (ClubOS/Square/ClubHub)
    ↓
System checks: "Which manager is logged in?"
    ↓
System retrieves THAT manager's credentials from database
    ↓
Uses those credentials for the API call
```

### Example:
```python
# When YOU are logged in:
manager_id = "your_manager_id"
credentials = get_credentials(manager_id)  # Gets YOUR Square token

# When TYLER is logged in:
manager_id = "tyler_manager_id"
credentials = get_credentials(manager_id)  # Gets TYLER's Square token
```

---

## 🔧 Technical Details

### Database Tables

**manager_credentials** table stores:
```sql
CREATE TABLE manager_credentials (
    id INTEGER PRIMARY KEY,
    manager_id TEXT UNIQUE,
    clubos_username TEXT,
    clubos_password TEXT (encrypted),
    clubhub_email TEXT,
    clubhub_password TEXT (encrypted),
    square_access_token TEXT (encrypted),
    square_location_id TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### Code Flow

1. **Login** → Session stores `manager_id`
2. **API Call** → Looks up credentials by `manager_id`
3. **Execute** → Uses that manager's credentials
4. **Logout** → Clears session

### Files Modified

- `templates/manager_credentials.html` - New UI for credential entry
- `src/routes/admin.py` - Routes for credentials CRUD
- `src/services/authentication/secure_secrets_manager.py` - Updated to use env vars as fallback

---

## 🧪 Testing the Setup

### Test Credentials Storage

1. Log in as yourself
2. Go to `/admin/credentials`
3. Enter test credentials
4. Click "Test Credentials" button
5. Should see: ✅ "Credentials test successful!"

### Test Multi-Manager

1. Create Tyler's account
2. Log out
3. Log in as Tyler
4. Go to `/admin/credentials`
5. Enter DIFFERENT credentials than yours
6. Save
7. Verify Tyler's Square transactions show HIS gym data, not yours

---

## 🎁 Benefits

✅ **No Code Changes Needed** - Tyler doesn't need to modify code
✅ **Secure** - Each manager's credentials are isolated
✅ **Easy Setup** - Just fill out a web form
✅ **Scalable** - Add 10 managers, 100 managers - same process
✅ **Audit Trail** - All credential changes are logged
✅ **FREE** - No Google Cloud billing required

---

## ❓ FAQs

**Q: Do I still need the .env file?**
A: Yes, for initial app startup. But once you enter credentials via the UI, those take precedence.

**Q: Can Tyler see my credentials?**
A: No, credentials are encrypted and isolated per manager.

**Q: What if I forget my credentials?**
A: You can update them anytime at `/admin/credentials`

**Q: Does this work offline?**
A: Yes, credentials are stored in the local SQLite database.

**Q: Can I export credentials?**
A: No, for security reasons. But you can always re-enter them.

---

## 🚨 Important Notes

1. **Backup the database** - Contains all credentials
2. **Don't commit .env to Git** - Already in `.gitignore`
3. **Use HTTPS in production** - Protects credentials in transit
4. **Rotate credentials periodically** - Security best practice

---

## 📞 Support

If Tyler has issues:
1. Check he's using correct manager_id
2. Verify credentials are saved (check database)
3. Test credentials using "Test" button
4. Check logs for authentication errors

---

**Generated:** 2025-10-03
**Version:** 1.0
**Status:** ✅ Complete
