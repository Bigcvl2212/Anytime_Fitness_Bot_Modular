# Gym Bot - Build & Distribution Guide

This guide explains how to build the Gym Bot installers for distribution to gym owners.

## Overview

The packaging system creates standalone installers that include:
- Python runtime
- All dependencies
- Application code
- Setup wizard for first-time configuration
- Desktop launcher for easy start/stop
- User documentation

## Prerequisites

### For Windows Builds

1. **Python 3.8+**
   - Download from https://python.org
   - Make sure to add Python to PATH during installation

2. **PyInstaller**
   - Will be installed automatically by build script
   - Or install manually: `pip install pyinstaller`

3. **Inno Setup** (for installer creation)
   - Download from https://jrsoftware.org/isdl.php
   - Install to default location
   - Version 6 recommended

4. **Visual C++ Redistributable**
   - Usually already installed
   - If needed: https://aka.ms/vs/17/release/vc_redist.x64.exe

### For macOS Builds

1. **Python 3.8+**
   - Install via Homebrew: `brew install python3`
   - Or download from https://python.org

2. **PyInstaller**
   - Will be installed automatically by build script
   - Or install manually: `pip3 install pyinstaller`

3. **create-dmg** (for DMG creation)
   - Install via Homebrew: `brew install create-dmg`
   - Or build script will attempt to install

4. **Xcode Command Line Tools**
   - Install: `xcode-select --install`

5. **Apple Developer Account** (optional, for code signing)
   - Required for notarization and distribution outside App Store
   - See: https://developer.apple.com

## Build Instructions

### Windows Build

#### Quick Build

1. Open Command Prompt in project directory
2. Run the build script:
   ```batch
   build_windows.bat
   ```

3. Wait for build to complete (5-10 minutes)
4. Find output in:
   - Executable: `dist\GymBot\GymBot.exe`
   - Installer: `Output\GymBotInstaller.exe`

#### Manual Build Steps

If you prefer to build manually:

```batch
# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build with PyInstaller
pyinstaller gym_bot.spec

# Create installer with Inno Setup
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_windows.iss
```

### macOS Build

#### Quick Build

1. Open Terminal in project directory
2. Make build script executable:
   ```bash
   chmod +x build_mac.sh
   ```

3. Run the build script:
   ```bash
   ./build_mac.sh
   ```

4. Wait for build to complete (5-10 minutes)
5. Find output in:
   - App Bundle: `dist/GymBot.app`
   - DMG Installer: `dist/GymBotInstaller.dmg`

#### Manual Build Steps

If you prefer to build manually:

```bash
# Install dependencies
pip3 install -r requirements.txt
pip3 install pyinstaller

# Build with PyInstaller
pyinstaller gym_bot.spec

# Create DMG (optional)
create-dmg \
  --volname "Gym Bot Installer" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --app-drop-link 600 185 \
  "dist/GymBotInstaller.dmg" \
  "dist/GymBot.app"
```

## File Structure

### Source Files

```
gym-bot-modular/
├── launcher.py              # Desktop launcher application
├── setup_wizard.py          # First-time setup GUI
├── run_dashboard.py         # Server entry point
├── gym_bot.spec            # PyInstaller configuration
├── installer_windows.iss   # Inno Setup script (Windows)
├── build_windows.bat       # Windows build script
├── build_mac.sh           # macOS build script
├── src/                   # Application source code
├── templates/            # Flask templates
├── static/              # Static assets
└── requirements.txt     # Python dependencies
```

### Build Output

```
dist/
├── GymBot/              # Windows executable folder
│   ├── GymBot.exe      # Main executable
│   ├── templates/      # Bundled templates
│   ├── static/        # Bundled static files
│   └── ...            # Libraries and dependencies
│
├── GymBot.app/         # macOS app bundle
│   └── Contents/
│       ├── MacOS/
│       ├── Resources/
│       └── Info.plist
│
Output/
└── GymBotInstaller.exe  # Windows installer
│
dist/
└── GymBotInstaller.dmg  # macOS disk image
```

## Customization

### Changing App Name/Version

Edit these files:

1. **gym_bot.spec**
   ```python
   name='YourAppName',
   ```

2. **installer_windows.iss**
   ```ini
   #define MyAppName "Your App Name"
   #define MyAppVersion "2.0.0"
   ```

3. **launcher.py**
   ```python
   self.root.title("Your App Name")
   ```

### Adding Custom Icons

**Windows:**
1. Create `favicon.ico` (256x256 recommended)
2. Place in `static/` folder
3. Update `gym_bot.spec`: `icon='static/favicon.ico'`

**macOS:**
1. Create `favicon.icns` from PNG using iconutil
2. Place in `static/` folder
3. Update `gym_bot.spec`: `icon='static/favicon.icns'`

### Modifying Setup Wizard

Edit `setup_wizard.py` to:
- Add/remove configuration pages
- Change credential requirements
- Customize UI appearance
- Add validation logic

## Code Signing

### Windows Code Signing

If you have a code signing certificate:

```batch
# Sign the executable
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\GymBot\GymBot.exe

# Sign the installer
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com Output\GymBotInstaller.exe
```

### macOS Code Signing

If you have an Apple Developer account:

```bash
# Sign the app
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: YOUR NAME" \
  dist/GymBot.app

# Notarize the app
xcrun notarytool submit dist/GymBotInstaller.dmg \
  --apple-id "your@email.com" \
  --password "app-specific-password" \
  --team-id "TEAM_ID" \
  --wait

# Staple the notarization
xcrun stapler staple dist/GymBot.app
```

## Testing

### Test Checklist

Before distributing, test:

- [ ] Installation on clean Windows machine
- [ ] Installation on clean macOS machine
- [ ] First-time setup wizard
- [ ] ClubOS credential validation
- [ ] Server start/stop functionality
- [ ] Browser auto-opening
- [ ] Dashboard login
- [ ] Data syncing
- [ ] All major features
- [ ] Uninstallation

### Test Environments

**Windows:**
- Windows 10 (fresh VM)
- Windows 11 (fresh VM)

**macOS:**
- macOS 10.13+ (fresh VM or test machine)

Use virtual machines or test machines without development tools installed.

## Distribution

### Windows Distribution

Distribute `Output\GymBotInstaller.exe`:
- File size: ~50-100 MB (depending on dependencies)
- Users just double-click to install
- Requires admin privileges for installation

### macOS Distribution

Distribute `dist/GymBotInstaller.dmg`:
- File size: ~50-100 MB (depending on dependencies)
- Users mount DMG and drag to Applications
- May require security approval on first launch

### Online Distribution

Options for distribution:
1. **Direct Download** - Host on your website
2. **Cloud Storage** - Google Drive, Dropbox, etc.
3. **GitHub Releases** - For version control
4. **App Store** - Requires additional work for macOS App Store

## Troubleshooting

### PyInstaller Issues

**Problem:** Import errors during build

**Solution:**
- Check `hiddenimports` in `gym_bot.spec`
- Add missing modules to hiddenimports list

**Problem:** Missing data files

**Solution:**
- Check `datas` in `gym_bot.spec`
- Add missing files/folders

### Windows Installer Issues

**Problem:** Inno Setup not found

**Solution:**
- Install Inno Setup 6
- Update path in `build_windows.bat` if installed elsewhere

### macOS DMG Issues

**Problem:** create-dmg fails

**Solution:**
- Install via Homebrew: `brew install create-dmg`
- Check disk space
- Ensure .app bundle is valid

### Runtime Issues

**Problem:** App won't start on user machine

**Solution:**
- Check Python version compatibility
- Ensure all dependencies are bundled
- Check for missing DLLs (Windows) or dylibs (macOS)
- Review logs in user's installation directory

## Advanced Configuration

### Optimization

**Reduce File Size:**
1. Exclude unnecessary packages in `gym_bot.spec`:
   ```python
   excludes=['matplotlib', 'numpy', 'scipy', 'pytest']
   ```

2. Use UPX compression:
   ```python
   upx=True,
   ```

3. Strip debug symbols:
   ```python
   strip=True,
   ```

**Faster Startup:**
1. Use onefile mode (single .exe):
   ```python
   # Change in gym_bot.spec
   exe = EXE(..., onefile=True, ...)
   ```

2. Optimize imports in Python code

### Multi-Version Support

To support multiple versions:

1. Use version tags in build output
2. Maintain separate installers per version
3. Implement auto-update checking in launcher

### Auto-Update

To add auto-update functionality:

1. Create version manifest (JSON)
2. Add update check to launcher.py
3. Download new installer automatically
4. Prompt user to update

## Support & Resources

### PyInstaller Documentation
https://pyinstaller.org/en/stable/

### Inno Setup Documentation
https://jrsoftware.org/ishelp/

### create-dmg Documentation
https://github.com/create-dmg/create-dmg

### Code Signing Resources
- Windows: https://docs.microsoft.com/en-us/windows/win32/seccrypto/signtool
- macOS: https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution

## Version History

- **v1.0.0** - Initial packaging system
  - PyInstaller configuration
  - Setup wizard
  - Desktop launcher
  - Windows and macOS installers
  - User documentation

---

For questions or issues with building, please contact the development team or create an issue in the repository.
