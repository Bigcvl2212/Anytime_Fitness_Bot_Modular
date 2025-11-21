#!/usr/bin/env python3
"""
Setup script for Tyler to run the Gym Bot locally
This script will:
1. Install required dependencies
2. Set up the database
3. Run the development server
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def install_requirements():
    """Install required Python packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def setup_database():
    """Set up the SQLite database"""
    print("🗄️ Setting up database...")
    try:
        # Create database if it doesn't exist
        if not os.path.exists("gym_bot.db"):
            # Run the database creation script
            subprocess.check_call([sys.executable, "create_local_db.py"])
            print("✅ Database created successfully")
        else:
            print("✅ Database already exists")
        return True
    except Exception as e:
        print(f"❌ Failed to setup database: {e}")
        return False

def create_startup_script():
    """Create a simple startup script for Tyler"""
    startup_script = """#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Set environment variables for local development
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'
os.environ['DB_TYPE'] = 'sqlite'

# Add project root and src to Python path
current_dir = Path(__file__).parent
project_root = str(current_dir)
src_path = str(current_dir / 'src')

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    # Import and run the app - try the main entry point first
    from run_dashboard import app
    if app:
        print("🚀 Starting Gym Bot Dashboard...")
        print("📱 Open your browser and go to: http://localhost:5000")
        print("🔐 You'll need to set up YOUR ClubOS credentials on first login")
        print("💡 Press Ctrl+C to stop the server")
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    else:
        raise ImportError("Could not create app from run_dashboard")
except ImportError:
    # Fallback to direct src import
    try:
        from src.main_app import create_app
        app = create_app()
        print("🚀 Starting Gym Bot Dashboard...")
        print("📱 Open your browser and go to: http://localhost:5000")
        print("🔐 You'll need to set up YOUR ClubOS credentials on first login")
        print("💡 Press Ctrl+C to stop the server")
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except Exception as e:
        print(f"❌ Failed to start app: {e}")
        print("💡 Make sure all files were extracted properly")
        sys.exit(1)
"""
    
    with open("start_gym_bot.py", "w") as f:
        f.write(startup_script)
    print("✅ Startup script created: start_gym_bot.py")

def create_readme():
    """Create a README for Tyler"""
    readme_content = """# Gym Bot Dashboard - Local Setup

## Quick Start
1. Make sure you have Python 3.11+ installed
2. Run: `python setup_for_tyler.py`
3. Run: `python start_gym_bot.py`
4. Open browser: http://localhost:5000

## Login Credentials
- Username: (Tyler will need to set this up)
- Password: (Tyler will need to set this up)

## Features Available
- Member management
- Training clients
- Collections management
- ClubOS integration
- Automated access control

## Troubleshooting
- If port 5000 is busy, the app will try other ports
- Check the console output for any error messages
- Make sure all files are in the same directory

## Stopping the App
Press Ctrl+C in the terminal to stop the server
"""
    
    with open("README_TYLER.md", "w") as f:
        f.write(readme_content)
    print("✅ README created: README_TYLER.md")

def main():
    """Main setup function"""
    print("🏋️‍♂️ Setting up Gym Bot for Tyler...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ Error: requirements.txt not found. Make sure you're in the gym-bot-modular directory")
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Setup database
    if not setup_database():
        return False
    
    # Create startup script
    create_startup_script()
    
    # Create README
    create_readme()
    
    print("\n🎉 Setup complete!")
    print("=" * 50)
    print("Tyler can now run: python start_gym_bot.py")
    print("The app will be available at: http://localhost:5000")
    
    return True

if __name__ == "__main__":
    main()

