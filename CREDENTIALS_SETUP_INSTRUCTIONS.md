# 🚨 URGENT: CREDENTIALS SETUP REQUIRED

## What I Fixed:
✅ **Database Schema** - prospects.prospect_id is now nullable (fixed constraint error)  
✅ **API Code** - Type handling for past-due status is correct  

## What YOU Need to Do:

### STEP 1: Stop the Server
Press `Ctrl+C` in the terminal running Flask

### STEP 2: Clear Python Cache (Windows PowerShell)
```powershell
# Stop the server first, then run:
Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force
```

### STEP 3: Fix ClubOS Credentials in `.env` file

**Open `.env` and replace these lines:**

**CURRENT (BROKEN):**
```env
CLUBOS_USERNAME=your_clubos_username_here
CLUBOS_PASSWORD=your_clubos_password_here
```

**CHANGE TO (with YOUR real ClubOS login):**
```env
CLUBOS_USERNAME=your_actual_clubos_username
CLUBOS_PASSWORD=your_actual_clubos_password
```

### STEP 4: Fix Square Location ID (if you use Square)

**CURRENT (BROKEN):**
```env
SQUARE_PRODUCTION_LOCATION_ID=your_square_location_id_here
```

**CHANGE TO (with your real Square location ID):**
```env
SQUARE_PRODUCTION_LOCATION_ID=YOUR_REAL_LOCATION_ID
```

**Don't have it?** You can get it from:
- Square Dashboard → Locations → Copy Location ID
- Or leave it as-is if you don't use Square payments

### STEP 5: Restart the Server
```powershell
python run_dashboard.py
```

---

## What Will Be Fixed After Restart:

✅ **"object of type 'int' has no len()" error** - Python cache cleared, new code loaded  
✅ **"NOT NULL constraint failed: prospects.prospect_id"** - Database schema fixed  
✅ **ClubOS authentication failures** - Will work once you add real credentials  
✅ **Event cards will show training status** - API errors resolved  

---

## Why This Happened:

1. **Python Cache Issue**: Windows locks `.pyc` files while Flask runs - must stop server to clear cache
2. **Database Schema**: `prospect_id` was NOT NULL but ClubHub API returns prospects without IDs sometimes
3. **Placeholder Credentials**: The `.env` file had placeholder values that can't authenticate

---

## If You Don't Know Your ClubOS Credentials:

1. Try logging into ClubOS manually: https://anytime.club-os.com
2. Use the same username/password in the `.env` file
3. If you don't have access, contact your gym's ClubOS administrator
