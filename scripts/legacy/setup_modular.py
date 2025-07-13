"""
Setup Script for Modular Gym Bot
Helps migrate from the monolithic script to the modular structure.
"""

import os
import shutil
import sys
from pathlib import Path

def create_directory_structure():
    """Create the complete directory structure."""
    directories = [
        "gym_bot",
        "gym_bot/config",
        "gym_bot/core", 
        "gym_bot/services",
        "gym_bot/services/ai",
        "gym_bot/services/clubos",
        "gym_bot/services/payments",
        "gym_bot/services/data",
        "gym_bot/workflows",
        "gym_bot/utils",
        "gym_bot/web",
        "tests",
        "debug",
        "package_data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def backup_original_files():
    """Backup original files before migration."""
    backup_dir = "backup_original"
    Path(backup_dir).mkdir(exist_ok=True)
    
    files_to_backup = [
        "Anytime_Bot.py",
        "requirements.txt",
        "master_contact_list.xlsx",
        "training_clients.csv"
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_dir, file))
            print(f"✅ Backed up: {file}")

def create_environment_files():
    """Create environment and configuration files."""
    
    # Create .env template
    env_content = """# Gym Bot Environment Configuration

# Square API Configuration
SQUARE_ENVIRONMENT=sandbox
SQUARE_LOCATION_ID=your_location_id_here

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=8080
FLASK_DEBUG=False

# Debug Configuration
DEBUG_MODE=True
"""
    
    with open(".env.template", "w") as f:
        f.write(env_content)
    print("✅ Created .env.template")
    
    # Create setup.py
    setup_content = """from setuptools import setup, find_packages

setup(
    name="gym-bot",
    version="2.0.0",
    description="Modular Gym Management Bot for Anytime Fitness",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "openpyxl>=3.1.0",
        "pandas",
        "numpy",
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.0",
        "beautifulsoup4>=4.12.0",
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "google-cloud-secret-manager",
        "google-cloud-firestore",
        "google-generativeai",
        "square",
        "Flask",
        "gunicorn"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "gym-bot=main:main",
        ],
    },
)
"""
    
    with open("setup.py", "w") as f:
        f.write(setup_content)
    print("✅ Created setup.py")

def create_readme():
    """Create comprehensive README for the modular system."""
    readme_content = """# Gym Bot - Modular System

A modular gym management system for Anytime Fitness, featuring automated messaging, payment processing, and member management.

## 🏗️ Architecture

The system is organized into the following modules:

### Core Modules
- **`config/`** - Configuration management and constants
- **`core/`** - WebDriver setup and authentication
- **`services/`** - External service integrations (AI, payments, ClubOS)
- **`workflows/`** - Business logic and automated workflows
- **`utils/`** - Debugging and utility functions
- **`web/`** - Flask web server and webhooks

### Service Integrations
- **ClubOS** - Gym management system integration
- **Square** - Payment processing and invoice management
- **Gemini AI** - Intelligent conversation generation
- **Google Cloud** - Secret management and Firestore

## 🚀 Quick Start

### Installation

1. **Clone or set up the repository:**
   ```bash
   cd gym-bot
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

3. **Configure Google Cloud secrets:**
   - Set up Google Cloud Secret Manager
   - Store your API keys and credentials

### Basic Usage

```bash
# Test all connections
python main.py --action test-connections

# Process incoming messages
python main.py --action process-messages

# Run payment workflows
python main.py --action process-payments
```

## 📁 File Structure

```
gym_bot/
├── config/
│   ├── constants.py           # Application constants
│   ├── secrets.py             # Secret management
│   └── settings.py            # Environment settings
├── core/
│   ├── driver.py              # WebDriver management
│   ├── authentication.py     # ClubOS authentication
│   └── base_scraper.py        # Base scraping functionality
├── services/
│   ├── ai/
│   │   └── gemini.py          # Gemini AI integration
│   ├── clubos/
│   │   ├── messaging.py       # ClubOS messaging
│   │   ├── calendar.py        # Calendar management
│   │   └── training.py        # Training client management
│   ├── payments/
│   │   ├── square_client.py   # Square API integration
│   │   └── invoice.py         # Invoice management
│   └── data/
│       ├── contacts.py        # Contact management
│       └── excel.py           # Excel operations
├── workflows/
│   ├── campaigns.py           # Marketing campaigns
│   ├── invoice_workflow.py    # Payment processing
│   └── training_workflow.py   # Training workflows
├── utils/
│   ├── debug.py               # Debug utilities
│   └── helpers.py             # Helper functions
└── web/
    ├── app.py                 # Flask application
    ├── routes.py              # Web routes
    └── webhooks.py            # Payment webhooks
```

## 🔧 Configuration

### Google Cloud Setup
1. Create a Google Cloud project
2. Enable Secret Manager API
3. Store the following secrets:
   - `clubos-username`
   - `clubos-password`
   - `gemini-api-key`
   - `square-sandbox-access-token`
   - `square-production-access-token`
   - `square-location-id`

### Square Setup
1. Create Square developer account
2. Generate API keys for sandbox/production
3. Store credentials in Google Cloud Secret Manager

## 🔄 Migration from Monolithic Script

The modular system is designed to be backwards compatible. Key functions have been extracted into appropriate modules:

- **Authentication** → `core.authentication`
- **Messaging** → `services.clubos.messaging`
- **Payments** → `services.payments.square_client`
- **AI Generation** → `services.ai.gemini`

## 🐛 Debugging

The system includes comprehensive debugging tools:

```python
from gym_bot.utils import debug_page_state

# Capture full page state for debugging
debug_info = debug_page_state(driver, "error_state")
```

Debug files are saved to the `debug/` folder with timestamps and detailed analysis.

## 🧪 Testing

```bash
# Test individual components
python -m pytest tests/

# Test service connections
python main.py --action test-connections
```

## 📈 Monitoring

- Debug logs are saved to `debug/gym_bot.log`
- Screenshots and HTML snapshots for troubleshooting
- Element analysis for page state debugging

## 🚨 Production Deployment

1. Set `SQUARE_ENVIRONMENT=production`
2. Update secrets with production API keys
3. Set `FLASK_DEBUG=False`
4. Use `gunicorn` for production WSGI server

## 📞 Support

For issues or questions:
1. Check the debug logs in `debug/`
2. Review the captured screenshots
3. Verify service connections with `test-connections`

---

**Note:** This modular system maintains all functionality from the original monolithic script while providing better organization, maintainability, and debugging capabilities.
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    print("✅ Created README.md")

def create_migration_script():
    """Create a script to help migrate existing data."""
    migration_content = """#!/usr/bin/env python3
\"\"\"
Migration Script for Gym Bot
Helps migrate data and settings from the old monolithic system.
\"\"\"

import os
import shutil
from pathlib import Path

def migrate_data_files():
    \"\"\"Migrate existing data files to the new structure.\"\"\"
    
    # Files that should be preserved
    data_files = [
        "master_contact_list.xlsx",
        "training_clients.csv",
        "client_secrets.json",
        "credentials.json",
        "token.json"
    ]
    
    for file in data_files:
        if os.path.exists(file):
            print(f"✅ Data file found: {file}")
        else:
            print(f"⚠️ Data file missing: {file}")
    
    print("\\n📋 Manual migration steps:")
    print("1. Ensure all data files are in the root directory")
    print("2. Update Google Cloud Secret Manager with your credentials")
    print("3. Test connections with: python main.py --action test-connections")
    print("4. Run a test workflow: python main.py --action process-messages")

def check_requirements():
    \"\"\"Check if all requirements are met.\"\"\"
    
    print("🔍 Checking requirements...")
    
    # Check Python version
    import sys
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    else:
        print(f"✅ Python version: {sys.version}")
    
    # Check required packages
    required_packages = [
        "selenium", "pandas", "requests", "google.cloud",
        "google.generativeai", "flask", "square"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\\n📦 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔄 MIGRATING TO MODULAR GYM BOT")
    print("="*50)
    
    if check_requirements():
        migrate_data_files()
        print("\\n✅ Migration check complete!")
        print("\\n🚀 Next steps:")
        print("1. Configure your .env file")
        print("2. Set up Google Cloud Secret Manager")
        print("3. Run: python main.py --action test-connections")
    else:
        print("\\n❌ Requirements not met - please install missing packages")
"""
    
    with open("migrate.py", "w") as f:
        f.write(migration_content)
    print("✅ Created migrate.py")

def main():
    """Main setup function."""
    print("🏗️ SETTING UP MODULAR GYM BOT")
    print("="*50)
    
    try:
        print("\n1. Creating directory structure...")
        create_directory_structure()
        
        print("\n2. Backing up original files...")
        backup_original_files()
        
        print("\n3. Creating environment files...")
        create_environment_files()
        
        print("\n4. Creating README...")
        create_readme()
        
        print("\n5. Creating migration script...")
        create_migration_script()
        
        print("\n✅ SETUP COMPLETE!")
        print("\n🚀 Next steps:")
        print("1. Review the created files")
        print("2. Configure your .env file")  
        print("3. Set up Google Cloud Secret Manager")
        print("4. Run: python migrate.py")
        print("5. Test: python main.py --action test-connections")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
