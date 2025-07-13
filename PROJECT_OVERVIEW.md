# Gym-Bot Project Overview for Dibyojyoti

## 🎯 Project Summary

This is a comprehensive gym management automation system for ClubHub integration. The bot handles automated token extraction, payment processing, member communication, and administrative tasks for Anytime Fitness Fond du Lac.

## 📁 Complete Project Structure

```
gym-bot-modular/
├── 📂 config/                    # Configuration and secrets
│   ├── constants.py              # Application constants
│   └── secrets.py                # API keys and credentials
├── 📂 core/                      # Core functionality
│   ├── authentication.py         # Authentication handling
│   └── driver.py                 # Web driver management
├── 📂 services/                  # Service layer (all integrations)
│   ├── ai/                      # Gemini AI integration
│   ├── api/                     # ClubHub, Square API clients
│   ├── authentication/           # Token extraction & management
│   ├── calendar/                # Calendar integration
│   ├── clubos/                  # ClubOS messaging
│   ├── data/                    # Data management & CSV handling
│   ├── notifications/           # Multi-channel notifications
│   └── payments/                # Square payment processing
├── 📂 workflows/                # Business logic workflows
│   ├── overdue_payments_optimized.py  # Main payment workflow
│   ├── member_messaging.py      # Communication workflows
│   └── data_management.py       # Data processing workflows
├── 📂 utils/                    # Utility functions
├── 📂 data/                     # Member data files
├── 📂 logs/                     # Application logs
├── 📂 docs/                     # Documentation
├── 📂 tests/                    # Test files
├── 📂 scripts/                  # Legacy scripts (archived)
├── 📂 backup/                   # Backup files
├── 📂 charles_session.chls/     # Charles Proxy session files
├── smart_token_capture.py       # 🚀 AUTOMATED TOKEN EXTRACTION
├── main.py                      # Application entry point
└── requirements.txt             # Dependencies
```

## 🔑 Key Features & Functionality

### 1. **Automated Token Extraction** ⭐ (NEWEST FEATURE)
- **File**: `smart_token_capture.py`
- **What it does**: Automatically starts Charles Proxy, monitors ClubHub traffic, saves sessions, and extracts authentication tokens
- **Status**: ✅ **FULLY WORKING** - This was the major breakthrough we just completed
- **How it works**: 
  1. Starts Charles Proxy automatically
  2. Waits for user to use ClubHub app
  3. Detects ClubHub traffic
  4. Automatically saves session file
  5. Extracts Bearer tokens and session cookies
  6. Stores tokens securely for bot use

### 2. **Payment Processing**
- **Files**: `workflows/overdue_payments_optimized.py`, `services/payments/`
- **What it does**: Detects overdue payments, creates Square invoices, sends payment reminders
- **Status**: ✅ **WORKING** - Fully integrated with Square API

### 3. **Member Communication**
- **Files**: `workflows/member_messaging.py`, `services/clubos/`
- **What it does**: Automated messaging through ClubOS platform
- **Status**: ✅ **WORKING** - Integrated with ClubOS messaging

### 4. **Data Management**
- **Files**: `services/data/`, `workflows/data_management.py`
- **What it does**: CSV import/export, member data synchronization
- **Status**: ✅ **WORKING** - Handles Excel and CSV files

### 5. **AI Integration**
- **Files**: `services/ai/`
- **What it does**: Gemini AI for intelligent conversation handling
- **Status**: ✅ **WORKING** - Integrated for automated responses

## 🚀 How to Run the Bot

### 1. **Token Extraction** (Required First Step)
```bash
cd gym-bot-modular
python smart_token_capture.py
```
- This will start Charles Proxy
- Use ClubHub app on your device
- Bot automatically extracts and stores tokens

### 2. **Main Bot**
```bash
python main.py
```

### 3. **Individual Workflows**
```bash
# Payment processing
python -m gym_bot.workflows.overdue_payments_optimized

# Member messaging
python -m gym_bot.workflows.member_messaging

# Data management
python -m gym_bot.workflows.data_management
```

## 🔧 Configuration

### Required API Keys (in `config/secrets.py`)
- **ClubHub API**: For member data
- **Square API**: For payment processing
- **ClubOS Credentials**: For messaging
- **Gemini AI**: For intelligent responses

### Important Files
- `config/constants.py`: Application settings
- `config/secrets.py`: API keys (you'll need to add these)
- `data/`: Member data files
- `logs/`: Application logs for debugging

## 📊 Current Status

### ✅ **WORKING FEATURES**
1. **Automated token extraction** - Fully automated Charles Proxy integration
2. **Payment processing** - Square integration for invoices and payments
3. **Member messaging** - ClubOS integration for communications
4. **Data management** - CSV/Excel import/export
5. **AI integration** - Gemini AI for intelligent responses
6. **Logging** - Comprehensive logging system
7. **Error handling** - Robust error handling throughout

### 🔄 **RECENT BREAKTHROUGHS**
- **Token extraction automation**: The bot now automatically saves Charles session files and extracts tokens without manual intervention
- **Header parsing**: Fixed the JSON structure parsing to handle Charles session files correctly
- **Modular architecture**: Clean, maintainable codebase

## 🎯 For Dibyojyoti

### **What You Need to Do**
1. **Set up API keys** in `config/secrets.py`
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Test token extraction**: Run `smart_token_capture.py`
4. **Test main workflows**: Run individual workflow files

### **Key Files to Understand**
- `smart_token_capture.py` - The automated token extraction system
- `workflows/overdue_payments_optimized.py` - Main payment processing workflow
- `services/authentication/clubhub_token_capture.py` - Token management
- `config/constants.py` - Application configuration

### **Architecture Overview**
- **Services Layer**: All external integrations (APIs, AI, etc.)
- **Workflows Layer**: Business logic and main processes
- **Core Layer**: Authentication and web driver management
- **Utils Layer**: Helper functions and utilities

### **Data Flow**
1. **Token Extraction** → Charles Proxy → ClubHub → Stored Tokens
2. **Payment Processing** → Member Data → Square API → Invoices
3. **Messaging** → ClubOS → Member Communications
4. **AI Integration** → Gemini AI → Intelligent Responses

## 📝 Notes for Development

- All old scripts are archived in `archive/` folder
- The modular structure makes it easy to add new features
- Comprehensive logging in `logs/` directory
- Test files available in `tests/` directory
- Documentation in `docs/` directory

## 🚨 Important Notes

1. **API Keys Required**: You'll need to add your own API keys to `config/secrets.py`
2. **Charles Proxy**: Required for token extraction (already configured)
3. **Data Files**: Member data is in `data/` directory
4. **Logs**: Check `logs/` for debugging information

---

**This is a complete, working gym management automation system ready for production use!** 🎉 