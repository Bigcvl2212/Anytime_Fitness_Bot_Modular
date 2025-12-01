# Detailed Google Cloud SQL Setup Instructions

## Prerequisites
1. A Google account
2. A Google Cloud project (we'll create one if needed)
3. Billing enabled (required for Cloud SQL, but $300 free credits available)

---

## Step 1: Access Google Cloud Console

1. **Go to Google Cloud Console**
   - Open your web browser
   - Visit: **https://console.cloud.google.com/**
   - Sign in with your Google account

2. **Accept Terms of Service** (if prompted)
   - You may see a terms of service page
   - Click "Accept" to continue

---

## Step 2: Create or Select a Project

### If you don't have a project yet:
1. **Look for the project selector** at the top of the page
   - It's usually near the "Google Cloud" logo
   - Shows "Select a project" or a project name

2. **Click on the project dropdown**
   - Click "NEW PROJECT"
   - Enter project name: `gym-bot-app` (or your preferred name)
   - Click "CREATE"
   - Wait for project creation (takes about 30 seconds)

### If you have an existing project:
1. **Select your project** from the dropdown at the top

---

## Step 3: Enable Billing (Required for Cloud SQL)

1. **Go to Billing**
   - In the left sidebar, click on "Billing" 
   - OR use this direct link: https://console.cloud.google.com/billing

2. **Set up billing account**
   - If you don't have billing enabled, you'll see a "Link a billing account" button
   - Click "LINK A BILLING ACCOUNT"
   - Follow the prompts to add a credit card
   - **Don't worry**: New users get $300 in free credits (covers months of usage)

---

## Step 4: Navigate to Cloud SQL

**Option A: Using the search bar (Easiest)**
1. At the top of the Google Cloud Console, there's a **search bar**
2. Type: `SQL` 
3. Click on **"SQL"** from the dropdown results
4. This takes you directly to the Cloud SQL page

**Option B: Using the navigation menu**
1. Click the **☰ hamburger menu** (3 horizontal lines) in the top-left corner
2. Scroll down to find **"Databases"** section
3. Click **"SQL"** under the Databases section

**Option C: Direct URL**
- Go directly to: **https://console.cloud.google.com/sql**

---

## Step 5: Enable Cloud SQL API (If Required)

If this is your first time using Cloud SQL:
1. You may see a page saying "Cloud SQL API" needs to be enabled
2. Click **"ENABLE"** button
3. Wait for the API to be enabled (takes 1-2 minutes)

---

## Step 6: Create the SQL Instance

1. **Look for the CREATE INSTANCE button**
   - It should be prominently displayed on the Cloud SQL page
   - Usually blue button that says "CREATE INSTANCE"
   - If you don't see it, make sure you're on the main SQL instances page

2. **Choose Database Engine**
   - Click **"Choose PostgreSQL"** 
   - (Not MySQL or SQL Server)

3. **Choose Instance Type**
   - Select **"Enterprise"** (standard option)
   - Click **"NEXT"** or **"Continue"**

---

## Step 7: Configure Your Instance

Fill out the instance details:

### Basic Information:
- **Instance ID**: `gym-bot-postgres`
- **Password**: Click "Generate" for a secure password, then **SAVE THIS PASSWORD**
- **Database version**: PostgreSQL 15 (or latest available)
- **Region**: Choose closest to your location (e.g., `us-central1` for central US)
- **Zonal availability**: Single zone (cheaper for development)

### Machine Configuration:
- **Machine type**: 
  - Click "CHANGE" next to machine type
  - Select **"Shared core"** 
  - Choose **"db-f1-micro"** (cheapest option - ~$7/month)
  - Click "DONE"

### Storage:
- **Storage type**: SSD
- **Storage capacity**: 10 GB
- **Enable automatic storage increases**: ✅ (checked)

### Connections:
- **Public IP**: ✅ (checked) - needed for external connections
- **Private IP**: ❌ (unchecked) - not needed for now
- **SSL mode**: Leave as default

### Backups:
- **Automated backups**: ✅ (checked) - recommended
- **Backup window**: Choose a time when you won't be using the database

---

## Step 8: Create the Instance

1. **Review your settings**
2. **Click "CREATE INSTANCE"** 
3. **Wait for creation** (takes 3-5 minutes)
   - You'll see a spinner/progress indicator
   - Don't close the browser tab

---

## Step 9: Get Connection Information

Once the instance is created:

1. **Click on your instance name** (`gym-bot-postgres`)
2. **Copy the Public IP address**
   - Look for "Public IP address" in the instance details
   - Copy this IP address - you'll need it later
   - Example: `34.123.45.67`

3. **Set up authorized networks**
   - Click on **"Connections"** tab on the left
   - Scroll to **"Authorized networks"**
   - Click **"ADD NETWORK"**
   - Name: `My Computer`
   - Network: We'll get your IP address in the next step

---

## Step 10: Get Your IP Address and Add It

1. **Find your public IP**
   - Go to: https://whatismyipaddress.com/
   - Copy the IP address shown
   - Example: `123.45.67.89`

2. **Add your IP to authorized networks**
   - Back in the Google Cloud Console
   - In the "Network" field, enter: `123.45.67.89/32` (replace with your actual IP)
   - Click **"SAVE"**

---

## Step 11: Create the Database

1. **Go to the Databases tab**
   - In your Cloud SQL instance, click **"Databases"** on the left
   
2. **Create database**
   - Click **"CREATE DATABASE"**
   - Database name: `gym_bot`
   - Click **"CREATE"**

---

## Step 12: Test Connection

Now run our setup script to test everything:

```bash
python setup_cloud_sql.py
```

The script will ask for:
- **Database Host**: Use the Public IP you copied (e.g., `34.123.45.67`)
- **Database Password**: The password you generated/saved earlier
- **Database Name**: `gym_bot`
- **Database User**: `postgres`

---

## Troubleshooting Common Issues

### "I don't see the CREATE INSTANCE button"
- Make sure you're at: https://console.cloud.google.com/sql
- Ensure you have a project selected (check the project dropdown at the top)
- Make sure billing is enabled for your project

### "Cloud SQL API is not enabled"
- Click "ENABLE API" and wait for it to complete
- Refresh the page

### "Connection refused" when testing
- Double-check your IP is in authorized networks
- Verify you're using the correct Public IP address
- Make sure you added `/32` to the end of your IP

### "Authentication failed"
- Verify the password is correct
- Make sure you're using username `postgres`

---

## What You'll Have After Setup

✅ Cloud SQL PostgreSQL instance running  
✅ Database `gym_bot` created  
✅ Your IP address authorized for access  
✅ Connection details ready for migration  

**Total cost: ~$7/month (covered by $300 free credits for months)**

---

## Next Steps After Cloud SQL is Ready

1. Run: `python setup_cloud_sql.py` to configure connection
2. Run: `python services/database_migration.py` to migrate data
3. Test your app with PostgreSQL

Let me know if you get stuck at any step!