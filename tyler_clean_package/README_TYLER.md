# 🏋️‍♂️ Gym Bot Dashboard - Local Setup Guide

## Quick Start (Easiest Method)

### Windows Users:
1. **Download and extract** the zip file to a folder (e.g., `C:\gym_bot\`)
2. **Double-click** `start_gym_bot.bat`
3. **Open your browser** and go to: `http://localhost:5000`

### Mac/Linux Users:
1. **Download and extract** the zip file to a folder (e.g., `~/gym_bot/`)
2. **Option A - Double-click**: Double-click `start_gym_bot.sh` (may need to allow in Security settings)
3. **Option B - Terminal**: Open Terminal, navigate to the folder, and run: `./start_gym_bot.sh`
4. **Option C - Manual**: Run `python3 setup_for_tyler.py` then `python3 start_gym_bot.py`
5. **Open your browser** and go to: `http://localhost:5000`

## Manual Setup (If needed)

1. **Install Python 3.11+** if not already installed
   - Download from: https://python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Open terminal/command prompt** in the extracted folder

3. **Run setup**: `python setup_for_tyler.py`

4. **Start the app**: `python start_gym_bot.py`

5. **Open browser**: Go to `http://localhost:5000`

## 🔐 Login Setup

**IMPORTANT**: You'll need to set up YOUR ClubOS credentials on first run.

### Setup Process:
1. **Use YOUR ClubOS Credentials**: Your gym's ClubOS username and password
2. **App will sync YOUR data**: Members, training clients, payments from YOUR gym
3. **Fresh start**: No existing data - starts clean for your gym

## 📱 Available Features

### ✅ Working Features:
- **Member Management**: View, search, and manage gym members
- **Training Clients**: Track personal training clients and packages
- **Collections Management**: Send past-due accounts to collections
- **ClubOS Integration**: Real-time data sync with ClubOS
- **Automated Access Control**: Automatic lock/unlock based on payment status
- **Dashboard Analytics**: Member statistics and insights

### 🔧 Admin Features:
- **Bulk Operations**: Mass check-ins, messaging, etc.
- **Data Export**: Export member lists and reports
- **System Monitoring**: Health checks and performance metrics

## 🗄️ Database

- **Local SQLite Database**: All data stored locally on your computer
- **Clean Setup**: Fresh database created for your gym (no existing data)
- **Internet Required**: Connects to ClubOS and ClubHub for your gym's data
- **Data Persistence**: Your data is saved between sessions

## 🌐 Network Access

- **Local Access**: `http://localhost:5000` (only on your computer)
- **Network Access**: `http://YOUR_IP:5000` (access from other devices on your network)
- **Port**: 5000 (default), will try other ports if busy

## 🔧 Troubleshooting

### Common Issues:

**"Python not found"**
- **Windows**: Install Python 3.11+ from python.org - Make sure to check "Add Python to PATH"
- **Mac**: Install Python 3.11+ from python.org OR use Homebrew: `brew install python@3.11`
- **Linux**: Use your package manager: `sudo apt install python3.11` (Ubuntu) or equivalent

**"Port 5000 is busy"**
- The app will automatically try other ports
- Look for the new port number in the console output

**"Module not found" errors**
- **Windows**: Run: `python setup_for_tyler.py` first
- **Mac/Linux**: Run: `python3 setup_for_tyler.py` first
- Make sure you're in the correct directory with all extracted files
- **Mac**: If you get permission errors, try: `chmod +x start_gym_bot.sh`

**"Database errors"**
- Delete `gym_bot.db` and restart
- The app will recreate the database automatically

### Mac-Specific Issues:

**"Permission denied" when running .sh file**
- Open Terminal and run: `chmod +x start_gym_bot.sh`
- Or run manually: `python3 setup_for_tyler.py` then `python3 start_gym_bot.py`

**"python3 command not found"**
- Install Python 3.11+ from python.org
- Or use Homebrew: `brew install python@3.11`
- Check if installed: `python3 --version`

**Security warnings about running downloaded scripts**
- Go to System Preferences > Security & Privacy
- Allow the script to run, or use the manual Terminal commands instead

**SSL Certificate errors**
- Update certificates: `/Applications/Python\ 3.11/Install\ Certificates.command`
- Or install manually: `pip3 install --upgrade certifi`

### Getting Help:
- Check the console output for error messages
- All errors are logged with detailed information
- Contact Jeremy if you need assistance

## 📊 Performance

- **Memory Usage**: ~200-500MB RAM
- **Disk Space**: ~100MB for the application
- **Startup Time**: 10-30 seconds
- **Data Sync**: Real-time with ClubOS (requires internet)

## 🔒 Security

- **Local Data**: All data stays on your computer
- **No Cloud Storage**: Nothing is uploaded to external servers
- **Secure Authentication**: Uses ClubOS authentication
- **Data Encryption**: Sensitive data is encrypted locally

## 📈 Updates

- **Manual Updates**: Download new zip file when available
- **Data Migration**: Your local data will be preserved
- **Backup**: Always backup your `gym_bot.db` file before updates

## 🎯 Tips for Best Performance

1. **Close other applications** when running the dashboard
2. **Use Chrome or Firefox** for best compatibility
3. **Keep the terminal open** while using the app
4. **Regular restarts** if the app becomes slow
5. **Check internet connection** for ClubOS sync

## 📞 Support

For technical support or questions:
- Check this README first
- Look at console output for error details
- Contact Jeremy for assistance

---

**Ready to start?** Double-click `start_gym_bot.bat` (Windows) or `start_gym_bot.sh` (Mac/Linux)!
