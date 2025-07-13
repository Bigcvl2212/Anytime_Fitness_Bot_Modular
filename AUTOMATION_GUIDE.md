# Automated Token Extraction System - Complete Guide

## Overview

This system provides **fully automated ClubHub token extraction** with minimal user intervention. The goal is to eliminate manual token management while keeping tokens fresh and valid.

## System Architecture

### 1. **Token Extraction Scripts** (Root Level)
- `complete_token_automation.py` - **RECOMMENDED** - Full automation system
- `continuous_token_monitor.py` - Real-time file monitoring
- `automated_charles_export.py` - Automated Charles export
- `extract_charles_session.py` - Manual session extraction
- `fully_automated_token_extraction.py` - Basic automation

### 2. **Existing Authentication Services** (gym_bot/services/authentication/)
- `clubhub_token_capture.py` - Main token capture service
- `automated_token_workflow.py` - Automated workflow
- `token_server.py` - Token server

## Recommended Setup: Minimal User Input

### **Option 1: Complete Automation (RECOMMENDED)**

**What you need to do once:**
1. Start Charles Proxy
2. Configure iPad to use Charles as proxy
3. Run the automation script

**What happens automatically:**
- Monitors for new Charles session files
- Triggers Charles exports automatically
- Extracts tokens from session files
- Validates tokens against ClubHub API
- Stores tokens securely
- Keeps tokens fresh automatically

**Command:**
```bash
python complete_token_automation.py
```

### **Option 2: Continuous Monitoring**

**What you need to do:**
1. Start Charles Proxy
2. Export sessions manually when needed
3. Run the monitor script

**What happens automatically:**
- Watches for new session files
- Extracts tokens immediately
- Validates and stores tokens

**Command:**
```bash
python continuous_token_monitor.py
```

### **Option 3: On-Demand Extraction**

**What you need to do:**
1. Export Charles session manually
2. Run extraction script

**What happens automatically:**
- Extracts tokens from session file
- Validates against API
- Stores tokens

**Command:**
```bash
python extract_charles_session.py
```

## Integration with Existing Bot System

### **Automatic Token Loading**

The bot automatically uses the latest tokens from `data/clubhub_tokens_latest.json`:

```python
# In gym_bot/services/data/clubhub_api.py
def _get_fresh_headers(self):
    """Get fresh headers with latest tokens"""
    tokens = self.token_capture.get_latest_valid_tokens()
    if tokens:
        return {
            "Authorization": f"Bearer {tokens['bearer_token']}",
            "Cookie": f"incap_ses_132_434694={tokens['session_cookie']}",
            # ... other headers
        }
```

### **Token Refresh Workflow**

The bot automatically refreshes tokens when they expire:

```python
# In gym_bot/services/authentication/clubhub_token_capture.py
def get_latest_valid_tokens(self):
    """Get latest valid tokens or trigger refresh"""
    tokens = self.load_latest_tokens()
    
    if not tokens or self._tokens_expired(tokens):
        # Trigger automated refresh
        self._trigger_automated_refresh()
        tokens = self.load_latest_tokens()
    
    return tokens
```

## Setup Instructions for Minimal User Input

### **Step 1: Initial Setup (One-time)**

1. **Install Dependencies:**
   ```bash
   pip install watchdog pywin32 psutil requests
   ```

2. **Configure Charles Proxy:**
   - Open Charles Proxy
   - Go to Proxy → SSL Proxying Settings
   - Check "Enable SSL Proxying"
   - Add `*` to capture all traffic

3. **Configure iPad:**
   - Settings → Wi-Fi → Tap "i" next to network
   - Configure Proxy → Manual
   - Server: Your computer's IP address
   - Port: 8888

4. **Install SSL Certificate on iPad:**
   - In Charles: Help → SSL Proxying → Install Charles Root Certificate
   - Follow instructions to install on iPad
   - Settings → General → VPN & Device Management → Trust certificate

### **Step 2: Start Automation**

**Option A: Complete Automation (Recommended)**
```bash
python complete_token_automation.py
```

**Option B: Background Service**
```bash
# Create a Windows service or scheduled task
python complete_token_automation.py
```

### **Step 3: Use ClubHub App**

- Open ClubHub app on iPad
- Use the app normally (refresh dashboard, view members, etc.)
- The automation system will automatically:
  - Detect new traffic
  - Export Charles sessions
  - Extract fresh tokens
  - Validate and store tokens

## Automation Features

### **Automatic Charles Export**
- Windows automation (Ctrl+E)
- Charles CLI commands
- REST API calls
- File monitoring for auto-saved sessions

### **Real-time Token Extraction**
- Monitors for `.chls` and `.chlz` files
- Extracts tokens from ZIP archives
- Validates against ClubHub API
- Stores with timestamps

### **Token Management**
- Automatic validation
- Secure storage
- Expiry detection
- Fresh token retrieval

## Integration Points

### **1. Bot Token Loading**
```python
# gym_bot/services/data/clubhub_api.py
from ..authentication.clubhub_token_capture import ClubHubTokenCapture

class EnhancedClubHubAPIService:
    def __init__(self):
        self.token_capture = ClubHubTokenCapture()
    
    def _get_fresh_headers(self):
        tokens = self.token_capture.get_latest_valid_tokens()
        # Use tokens automatically
```

### **2. Automated Token Refresh**
```python
# gym_bot/services/authentication/clubhub_token_capture.py
def _trigger_automated_refresh(self):
    """Trigger automated token refresh"""
    import subprocess
    subprocess.run(["python", "complete_token_automation.py"], 
                   capture_output=True, timeout=60)
```

### **3. Background Monitoring**
```python
# Add to main bot workflow
def ensure_fresh_tokens():
    """Ensure tokens are fresh before operations"""
    token_capture = ClubHubTokenCapture()
    tokens = token_capture.get_latest_valid_tokens()
    
    if not tokens:
        # Trigger automated refresh
        subprocess.run(["python", "complete_token_automation.py"])
```

## User Workflow (Minimal Input)

### **Daily Operation:**
1. **Start Charles Proxy** (if not already running)
2. **Run automation script:** `python complete_token_automation.py`
3. **Use ClubHub app** on iPad normally
4. **Tokens are automatically extracted and refreshed**

### **When Tokens Expire:**
1. **Automation detects expiry** automatically
2. **Triggers fresh extraction** automatically
3. **Bot continues working** with new tokens

### **Troubleshooting:**
1. **Check Charles is running:** `tasklist | findstr Charles`
2. **Check automation is running:** Look for automation output
3. **Manual extraction if needed:** `python extract_charles_session.py`

## File Structure

```
gym-bot/
├── complete_token_automation.py     # Main automation script
├── continuous_token_monitor.py      # File monitoring
├── automated_charles_export.py      # Charles export automation
├── extract_charles_session.py       # Manual extraction
├── data/
│   ├── clubhub_tokens_latest.json  # Latest tokens
│   └── clubhub_tokens_YYYYMMDD_HHMMSS.json  # Timestamped tokens
├── charles_session.chls/           # Charles session files
└── gym_bot/
    └── services/
        └── authentication/
            ├── clubhub_token_capture.py      # Token capture service
            ├── automated_token_workflow.py    # Automated workflow
            └── token_server.py               # Token server
```

## Benefits

✅ **Zero manual token management**  
✅ **Automatic token refresh**  
✅ **Real-time monitoring**  
✅ **Seamless bot integration**  
✅ **Fault-tolerant operation**  
✅ **Secure token storage**  

## Next Steps

1. **Run the complete automation script**
2. **Test with ClubHub app usage**
3. **Verify tokens are automatically extracted**
4. **Integrate with existing bot workflows**

The system is designed to require **minimal user input** while providing **maximum automation** for token extraction and management. 