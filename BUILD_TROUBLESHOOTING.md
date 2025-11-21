# Build Troubleshooting Guide

## 🚀 Quick Start

### Before Building
1. **Run pre-flight check**: `python test_build.py`
2. **Fix any errors** before proceeding
3. **Build**: `build_windows.bat`

### Testing the Build
1. Navigate to: `dist\GymBot\`
2. Run: `GymBot.exe`
3. Check console output for errors
4. Check logs: `%LOCALAPPDATA%\GymBot\logs\launcher_flask.log`

---

## ❌ Common Build Failures & Fixes

### Issue 1: "ModuleNotFoundError: No module named 'src'"
**Cause**: PyInstaller didn't bundle the src package correctly

**Fix**:
- Verify `src/__init__.py` exists
- Check `gym_bot.spec` includes: `hiddenimports += collect_submodules('src')`
- Clean rebuild: Delete `build/` and `dist/` folders, rebuild

### Issue 2: "Failed to execute script 'launcher'"
**Cause**: Missing dependencies in the frozen bundle

**Fix**:
- Run: `python test_build.py` to identify missing imports
- Add missing imports to `gym_bot.spec` hiddenimports section
- Rebuild with `--clean` flag

### Issue 3: "Cannot find templates/dashboard.html"
**Cause**: Templates folder not bundled correctly

**Fix**:
- Check `gym_bot.spec` line: `datas += [('templates', 'templates')]`
- Verify `templates/` folder exists in project root
- Templates should be bundled into `dist\GymBot\_internal\`

### Issue 4: "Server failed to start within 30 seconds"
**Cause**: Flask app crashed on startup

**Fix**:
1. Enable console in `gym_bot.spec`: `console=True`
2. Rebuild and run `GymBot.exe`
3. Read error messages in console
4. Check logs: `%LOCALAPPDATA%\GymBot\logs\launcher_flask.log`

### Issue 5: "ImportError: cannot import name 'SocketIO'"
**Cause**: flask-socketio not installed or not bundled

**Fix**:
```bash
pip install flask-socketio python-socketio eventlet
```
Then rebuild. Verify `gym_bot.spec` includes:
```python
hiddenimports += collect_submodules('flask_socketio')
hiddenimports += collect_submodules('socketio')
hiddenimports += collect_submodules('eventlet')
```

### Issue 6: "Database is locked" or "Permission denied"
**Cause**: Database in read-only location (Program Files)

**Fix**: Already handled - database auto-creates in `%LOCALAPPDATA%\GymBot\data\`

### Issue 7: Build succeeds but exe shows blank window
**Cause**: Tkinter/GUI issue

**Fix**:
- Verify tkinter is installed: `python -m tkinter`
- Rebuild with console enabled to see errors
- Check that `launcher.py` is the entry point in `gym_bot.spec`

---

## 🔍 Debugging Steps

### Step 1: Enable Console Output
Edit `gym_bot.spec`:
```python
console=True,  # Change from False
```
Rebuild. Now you'll see error messages when running `GymBot.exe`

### Step 2: Check Import Paths
Run in frozen mode:
```python
import sys
print("Frozen:", getattr(sys, 'frozen', False))
print("MEIPASS:", getattr(sys, '_MEIPASS', 'N/A'))
print("sys.path:", sys.path)
```

### Step 3: Verify Bundle Contents
Check `dist\GymBot\_internal\` folder contains:
- `templates/` folder with HTML files
- `static/` folder with CSS/JS/images
- `run_dashboard.py`
- `src/` package folder

### Step 4: Test Individual Components
Before building, test each component works:
```bash
# Test Flask app
python run_dashboard.py

# Test launcher (script mode)
python launcher.py

# Test imports
python test_build.py
```

---

## 🐛 Advanced Debugging

### Enable PyInstaller Debug Mode
```bash
python -m PyInstaller gym_bot.spec --clean --debug all
```
This creates verbose logs in `build/` folder

### Check Missing Dependencies
After build fails, check `build\GymBot\warn-GymBot.txt` for:
- Missing modules
- Import errors
- Hidden imports needed

### Analyze Import Graph
```bash
pyi-archive_viewer dist\GymBot\GymBot.exe
```
This shows all files bundled in the exe

### Test in Python Console
```python
import sys
sys.frozen = True
sys._MEIPASS = r"C:\path\to\dist\GymBot"
from src.main_app import create_app
app = create_app()
```

---

## ✅ Build Checklist

Before each build:
- [ ] Run `python test_build.py` - all checks pass
- [ ] `src/__init__.py` exists
- [ ] `templates/` folder exists with HTML files
- [ ] `static/` folder exists
- [ ] `requirements.txt` up to date
- [ ] `.env` file created (or environment variables set)
- [ ] Delete `build/` and `dist/` folders
- [ ] Run `build_windows.bat`
- [ ] Test `dist\GymBot\GymBot.exe` manually
- [ ] Check logs in `%LOCALAPPDATA%\GymBot\logs\`

---

## 🔧 Quick Fixes

### Clean Everything
```batch
rmdir /s /q build dist
del /q *.spec
pip uninstall pyinstaller -y
pip install pyinstaller
python -m PyInstaller gym_bot.spec --clean --noconfirm
```

### Reinstall All Dependencies
```batch
pip uninstall -r requirements.txt -y
pip install -r requirements.txt --force-reinstall
```

### Test Without Building
```batch
python launcher.py
```
If this works but the built exe doesn't, it's a bundling issue.

---

## 📞 Still Not Working?

1. **Enable console output** in `gym_bot.spec` (console=True)
2. **Run the exe** and copy the error message
3. **Check logs**: `%LOCALAPPDATA%\GymBot\logs\launcher_flask.log`
4. **Verify** all files bundled: Check `dist\GymBot\_internal\`
5. **Test imports**: `python test_build.py`

### Log Locations
- Launcher log: `%LOCALAPPDATA%\GymBot\logs\launcher_flask.log`
- Dashboard log: `%LOCALAPPDATA%\GymBot\logs\dashboard.log`
- Build warnings: `build\GymBot\warn-GymBot.txt`
- PyInstaller log: Console output during build

### Common Environment Issues
- **Python version**: Must be 3.8+ (check: `python --version`)
- **Pip version**: Update with `python -m pip install --upgrade pip`
- **Virtual environment**: Deactivate if using one (may cause path issues)
- **Antivirus**: May block PyInstaller or the built exe

---

## 🎯 Success Indicators

Your build is successful when:
1. ✅ `dist\GymBot\GymBot.exe` exists
2. ✅ Running exe shows launcher window
3. ✅ Click "Start Server" - status turns green
4. ✅ Browser opens to http://localhost:5000
5. ✅ Dashboard loads with login screen
6. ✅ No errors in `%LOCALAPPDATA%\GymBot\logs\`

---

## 📚 Reference

### Key Files
- `launcher.py` - GUI that starts Flask
- `run_dashboard.py` - Flask app entry point
- `src/main_app.py` - Flask app factory
- `gym_bot.spec` - PyInstaller configuration

### Build Process
1. PyInstaller reads `gym_bot.spec`
2. Analyzes `launcher.py` imports
3. Bundles Python interpreter + dependencies
4. Creates `dist\GymBot\GymBot.exe`
5. Inno Setup packages as installer (optional)

### Frozen Mode Detection
```python
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    app_dir = sys._MEIPASS
else:
    # Running as script
    app_dir = os.path.dirname(__file__)
```
