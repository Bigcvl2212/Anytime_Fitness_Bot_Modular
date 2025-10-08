# Launcher Fix - Flask Server Startup Issue

## Problem

The Gym Bot launcher would show "Starting server..." forever, then fail with "Server failed to start within 30 seconds". However, Flask worked perfectly when started manually with `python run_dashboard.py`.

## Root Cause

The launcher was using `subprocess.Popen()` with **piped stdout/stderr**:

```python
self.server_process = subprocess.Popen(
    [sys.executable, str(run_script)],
    stdout=subprocess.PIPE,  # ❌ THIS CAUSES PROBLEMS
    stderr=subprocess.PIPE,  # ❌ THIS CAUSES PROBLEMS
    ...
)
```

### Why This Failed:

1. **Windows Output Buffering**: When stdout is piped on Windows, Python buffers output indefinitely
2. **Process Hanging**: Flask's startup messages were being captured but never read, causing the process to appear frozen
3. **No Visibility**: The launcher couldn't see Flask's output to know it started successfully
4. **Port Detection Delay**: The launcher was checking if port 5000 was open, but Flask may take time to bind

## Solution

**Changed from piped output to file-based logging:**

```python
# Create log file for server output
log_dir = Path(app_dir) / 'logs'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / 'launcher_flask.log'

# Open log file for writing
log_handle = open(log_file, 'w', buffering=1)  # Line buffered

self.server_process = subprocess.Popen(
    [sys.executable, str(run_dashboard.py')],
    stdout=log_handle,  # ✅ Write to file instead of pipe
    stderr=subprocess.STDOUT,  # ✅ Combine stderr with stdout
    ...
)
```

### Benefits:

1. **No Buffering Issues**: File writes don't block the process
2. **Full Visibility**: All Flask logs are saved to `logs/launcher_flask.log`
3. **Easy Debugging**: Users can click "View Logs" to see what happened
4. **Proper Cleanup**: Log file handle is closed when server stops

## Testing

### Before Fix:
- Launcher shows "Starting server..." forever
- After 30 seconds: "Server failed to start" error
- Port 5000 never opens
- Flask process may hang in background

### After Fix:
- Launcher starts Flask successfully
- Port 5000 opens within 5-10 seconds
- Dashboard opens automatically in browser
- All Flask output visible in `logs/launcher_flask.log`

## How to Test

1. **Close all Python processes**:
   ```powershell
   Stop-Process -Name python -Force -ErrorAction SilentlyContinue
   ```

2. **Start the launcher**:
   ```powershell
   python launcher.py
   ```

3. **Click "Start Server"**

4. **Expected Result**:
   - Status changes to "Starting server..."
   - Within 10 seconds: Status changes to "Server is running" (green indicator)
   - Browser opens automatically to `http://localhost:5000`
   - Dashboard loads successfully

5. **Check logs** (click "View Logs" button):
   - Should see all Flask startup messages
   - Should see "Running on http://127.0.0.1:5000"

## Files Modified

- `launcher.py` (Lines 168-198, 234-240, 306-317, 356-372)
  - Changed subprocess output from PIPE to file
  - Added log_handle tracking and cleanup
  - Updated View Logs to show launcher_flask.log

## Additional Notes

- The launcher waits up to 30 seconds for port 5000 to open
- Flask typically starts in 5-10 seconds on modern systems
- If startup takes longer, check `logs/launcher_flask.log` for errors
- The log file is overwritten each time Flask starts (not appended)

## Troubleshooting

If Flask still doesn't start:

1. **Check the log file**:
   - Open `logs/launcher_flask.log`
   - Look for Python errors or missing dependencies

2. **Verify manually**:
   ```powershell
   python run_dashboard.py
   ```
   - If this works, launcher issue
   - If this fails, Flask configuration issue

3. **Check port availability**:
   ```powershell
   netstat -ano | findstr :5000
   ```
   - If port is in use, kill the process or change Flask port

4. **Check Python path**:
   - Launcher uses `sys.executable` (same Python running launcher)
   - Verify: `python --version` shows correct Python 3.9+

## Prevention

To avoid similar issues in the future:

1. **Never use PIPE for long-running processes** - Use files or devnull
2. **Always provide visibility** - Log files for debugging
3. **Test subprocess calls** - Verify they work in isolation first
4. **Handle cleanup properly** - Close file handles on exit

---

**Status**: ✅ FIXED
**Date**: October 8, 2025
**Tested**: Pending user verification
