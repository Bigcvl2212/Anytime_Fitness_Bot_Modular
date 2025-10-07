# Gym Bot Dashboard - Quick Start Guide

Welcome to Gym Bot! This guide will help you install and start using the dashboard in minutes.

## Table of Contents
1. [Installation](#installation)
2. [First-Time Setup](#first-time-setup)
3. [Starting the Dashboard](#starting-the-dashboard)
4. [Using the Dashboard](#using-the-dashboard)
5. [Troubleshooting](#troubleshooting)
6. [Support](#support)

---

## Installation

### Windows Installation

1. **Download the Installer**
   - Download `GymBotInstaller.exe` from your distribution source
   - Save it to your Downloads folder

2. **Run the Installer**
   - Double-click `GymBotInstaller.exe`
   - Click "Yes" if Windows asks for permission
   - Follow the installation wizard
   - Choose your installation location (default is recommended)
   - Click "Install"

3. **Complete Installation**
   - Wait for the installation to complete
   - Choose whether to create a desktop shortcut
   - Click "Finish"

### macOS Installation

1. **Download the DMG**
   - Download `GymBotInstaller.dmg` from your distribution source
   - Save it to your Downloads folder

2. **Install the Application**
   - Double-click `GymBotInstaller.dmg` to mount it
   - Drag the "Gym Bot" icon to the Applications folder
   - Eject the DMG installer

3. **First Launch (Security)**
   - Right-click "Gym Bot" in Applications
   - Select "Open" (required for first launch only)
   - Click "Open" in the security dialog

---

## First-Time Setup

When you launch Gym Bot for the first time, you'll see the Setup Wizard.

### Step 1: Welcome Screen
- Read the welcome message
- Click "Next" to begin setup

### Step 2: ClubOS Integration (Required)

Gym Bot needs your ClubOS credentials to access member data.

1. **Enter Your ClubOS Username**
   - This is the username you use to log into ClubOS
   - Example: `john.smith@anytimefitness.com`

2. **Enter Your ClubOS Password**
   - Your ClubOS password
   - This is stored securely and encrypted

3. **Test Connection**
   - Click "Test Connection" to verify credentials
   - Wait for confirmation (green checkmark)
   - If it fails, double-check your credentials

4. Click "Next" to continue

### Step 3: Square Integration (Optional)

If you want to send invoices through Square:

1. **Get Your Square Credentials**
   - Go to https://developer.squareup.com/apps
   - Sign in with your Square account
   - Create a new application or select existing
   - Copy your "Access Token"
   - Copy your "Location ID"

2. **Enter Credentials**
   - Paste Access Token
   - Paste Location ID

3. Click "Next" (or "Skip" if not using Square)

### Step 4: AI Features (Optional)

For AI-powered insights and automation:

1. **Get OpenAI API Key**
   - Go to https://platform.openai.com/api-keys
   - Sign in or create account
   - Click "Create new secret key"
   - Copy the key

2. **Enter API Key**
   - Paste your OpenAI API key

3. Click "Next" (or "Skip" if not using AI)

### Step 5: Review & Save

1. **Review Your Settings**
   - Check that all credentials are correct
   - Configured items will show "Configured"
   - Skipped items will show "Not configured"

2. **Save Configuration**
   - Click "Save & Launch"
   - Gym Bot will save your settings
   - The dashboard will start automatically

---

## Starting the Dashboard

### Launching Gym Bot

**Windows:**
- Double-click the "Gym Bot" icon on your desktop, or
- Go to Start Menu → Gym Bot

**macOS:**
- Open Applications folder
- Double-click "Gym Bot"

### Using the Launcher

The Gym Bot Launcher window will appear:

1. **Start the Server**
   - Click the "Start Server" button
   - Wait for status to change to "Server is running"
   - The indicator will turn green

2. **Open Dashboard**
   - Click "Open Dashboard" button, or
   - The browser will open automatically
   - Navigate to `http://localhost:5000`

3. **Login**
   - Enter your admin credentials
   - If first time, default admin account will be created
   - Follow prompts to change password

### Stopping the Dashboard

When you're done:

1. Click "Stop Server" in the Launcher
2. Confirm the action
3. Wait for server to stop
4. Close the Launcher window

**Important:** Always stop the server before shutting down your computer!

---

## Using the Dashboard

### Dashboard Overview

After logging in, you'll see the main dashboard with:

- **Member Count** - Total active members
- **Training Clients** - Active training clients
- **Prospects** - Current prospects
- **Recent Activity** - Latest member activities

### Key Features

#### 1. Members Management
- View all gym members
- See membership status and billing info
- Track check-ins and attendance
- View member details and history

#### 2. Training Clients
- Manage personal training clients
- Track training packages and sessions
- Monitor payment status
- Send invoices for past-due clients

#### 3. Messaging
- Send messages to members through ClubOS
- View message history
- Bulk messaging capabilities
- Automated follow-ups

#### 4. Prospects
- Track potential new members
- Follow up with prospects
- Convert prospects to members
- Monitor sales pipeline

#### 5. Analytics
- View membership trends
- Track revenue
- Analyze attendance patterns
- Generate reports

### Common Tasks

#### Send a Message to a Member

1. Click "Messaging" in the sidebar
2. Click "New Message"
3. Select recipient
4. Type your message
5. Click "Send"

#### Check Training Client Status

1. Click "Training Clients" in sidebar
2. Use search bar to find client
3. Click on client name
4. View package status and payment info

#### Send Past-Due Invoice

1. Go to Training Clients
2. Filter by "Past Due"
3. Click on client
4. Click "Send Invoice"
5. Review and confirm

---

## Troubleshooting

### Server Won't Start

**Problem:** Click "Start Server" but nothing happens

**Solutions:**
1. Check that port 5000 isn't already in use
2. Close any other web applications
3. Restart your computer
4. View logs (click "View Logs" in Launcher)

### Can't Login to Dashboard

**Problem:** Invalid credentials error

**Solutions:**
1. Default admin username is usually `admin`
2. Check that you've completed first-time setup
3. Try resetting your password (contact support)
4. Check ClubOS credentials in settings

### ClubOS Connection Failed

**Problem:** Can't sync data from ClubOS

**Solutions:**
1. Click "Settings" in Launcher
2. Re-run setup wizard
3. Test ClubOS credentials
4. Verify your ClubOS account is active
5. Check your internet connection

### Browser Won't Open

**Problem:** Dashboard doesn't open automatically

**Solutions:**
1. Manually open browser
2. Navigate to `http://localhost:5000`
3. Make sure server is running (green indicator)
4. Try different browser (Chrome recommended)

### Data Not Syncing

**Problem:** Member data is old or missing

**Solutions:**
1. Click "Refresh Data" in dashboard
2. Wait for sync to complete
3. Check ClubOS credentials
4. View logs for errors

---

## Settings & Configuration

### Changing Your Settings

1. Open Gym Bot Launcher
2. Click "Settings" button
3. Setup wizard will open
4. Update any credentials
5. Click "Save & Launch"

### Viewing Logs

1. Open Gym Bot Launcher
2. Click "View Logs"
3. Log file will open in text editor
4. Search for errors or warnings
5. Send logs to support if needed

### Updating Gym Bot

When a new version is available:

1. Download new installer
2. Run installer (will upgrade automatically)
3. Your data and settings are preserved
4. Restart Gym Bot

---

## Data & Security

### Where is My Data Stored?

- **Local Database:** All data is stored locally on your computer
- **Location:** `C:\Program Files\GymBot\data\` (Windows) or `~/Applications/GymBot.app/data/` (Mac)
- **Backups:** Automatic backups created daily

### Is My Data Secure?

- All credentials are encrypted
- Passwords are hashed and never stored in plain text
- Database is protected with encryption at rest
- Communication with ClubOS/Square uses HTTPS
- No data is sent to third parties (except API providers you configure)

### Backing Up Your Data

**Automatic Backups:**
- Created daily automatically
- Stored in `backups` folder
- Last 7 days retained

**Manual Backup:**
1. Navigate to installation folder
2. Copy the `data` folder
3. Save to external drive or cloud storage

---

## Support

### Getting Help

**Documentation:**
- This Quick Start Guide
- In-app help tooltips
- Online knowledge base

**Contact Support:**
- Email: support@gymbot.com
- Phone: 1-800-GYM-BOTS
- Live chat: Available in dashboard

**Community:**
- User forums: https://community.gymbot.com
- Video tutorials: https://youtube.com/gymbot
- Facebook group: Gym Bot Users

### Providing Feedback

We'd love to hear from you!

1. Click "Help" in dashboard
2. Select "Send Feedback"
3. Describe your experience
4. Submit

---

## Tips for Success

### Best Practices

1. **Daily Routine**
   - Start Gym Bot when you open
   - Review dashboard for updates
   - Check messages regularly
   - Stop server when done

2. **Data Management**
   - Sync data at start of day
   - Review member status weekly
   - Send invoices promptly
   - Back up data monthly

3. **Communication**
   - Respond to messages quickly
   - Follow up with prospects
   - Send reminders for past-due clients
   - Use templates for common messages

4. **Performance**
   - Close unused browser tabs
   - Clear cache periodically
   - Keep Gym Bot updated
   - Restart server weekly

---

## Frequently Asked Questions

**Q: Can multiple people use Gym Bot at the same time?**
A: No, Gym Bot runs locally on one computer. For multi-user access, contact us about our cloud version.

**Q: Does Gym Bot work offline?**
A: Limited functionality. You can view cached data, but syncing with ClubOS requires internet.

**Q: How often does data sync?**
A: Automatically every 5 minutes while running. You can manually refresh anytime.

**Q: Can I customize the dashboard?**
A: Yes! Contact support for customization options.

**Q: Is there a mobile app?**
A: Not currently, but Gym Bot works great in mobile browsers.

---

## Appendix

### System Requirements

**Windows:**
- Windows 10 or higher
- 4GB RAM minimum (8GB recommended)
- 500MB disk space
- Internet connection

**macOS:**
- macOS 10.13 or higher
- 4GB RAM minimum (8GB recommended)
- 500MB disk space
- Internet connection

### Keyboard Shortcuts

- `Ctrl/Cmd + R` - Refresh data
- `Ctrl/Cmd + N` - New message
- `Ctrl/Cmd + F` - Search
- `Ctrl/Cmd + ,` - Settings

---

**Thank you for using Gym Bot!**

We're committed to helping you manage your gym more efficiently. If you have any questions or need assistance, don't hesitate to reach out to our support team.

*Version 1.0.0 - Updated October 2025*
