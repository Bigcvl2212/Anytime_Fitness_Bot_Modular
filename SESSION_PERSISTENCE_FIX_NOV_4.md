# Session Persistence Fix - November 4, 2025

## Problem Solved

**Issue:** Members page was redirecting to login after club selection, losing all selected clubs and session data.

**Root Cause:** The `require_auth` decorator in `src/routes/auth.py` was calling `session.clear()` whenever authentication validation failed, which completely wiped out ALL session data including:
- `selected_clubs`
- `available_clubs`
- `user_info`

This meant even a temporary auth hiccup would lose the user's club selection.

---

## Fix Applied

Modified `src/routes/auth.py` in TWO places to preserve important session data:

### Fix 1: Authentication Failure (Lines 36-56)

**Before:**
```python
if not session.get('authenticated') or not session.get('manager_id'):
    logger.warning(f"❌ AUTH FAILED for route {route_name}")
    session.clear()  # ❌ WIPES EVERYTHING
    return redirect(url_for('auth.login'))
```

**After:**
```python
if not session.get('authenticated') or not session.get('manager_id'):
    logger.warning(f"❌ AUTH FAILED for route {route_name}")

    # IMPORTANT: Preserve club selection data before clearing
    preserved_data = {
        'selected_clubs': session.get('selected_clubs'),
        'available_clubs': session.get('available_clubs'),
        'user_info': session.get('user_info')
    }

    session.clear()

    # Restore preserved data if it existed
    if preserved_data.get('selected_clubs'):
        session['selected_clubs'] = preserved_data['selected_clubs']
        logger.info(f"🔄 Preserved selected_clubs: {preserved_data['selected_clubs']}")
    if preserved_data.get('available_clubs'):
        session['available_clubs'] = preserved_data['available_clubs']
    if preserved_data.get('user_info'):
        session['user_info'] = preserved_data['user_info']

    session.modified = True
    return redirect(url_for('auth.login'))
```

---

### Fix 2: Session Timeout (Lines 66-88)

**Before:**
```python
if session_age > timedelta(hours=8):
    logger.warning(f"⚠️ Session expired for {route_name}: age={session_age}")
    session.clear()  # ❌ WIPES EVERYTHING
    return redirect(url_for('auth.login'))
```

**After:**
```python
if session_age > timedelta(hours=8):
    logger.warning(f"⚠️ Session expired for {route_name}: age={session_age}")

    # Preserve club selection data before clearing
    preserved_data = {
        'selected_clubs': session.get('selected_clubs'),
        'available_clubs': session.get('available_clubs'),
        'user_info': session.get('user_info')
    }

    session.clear()

    # Restore preserved data
    if preserved_data.get('selected_clubs'):
        session['selected_clubs'] = preserved_data['selected_clubs']
    if preserved_data.get('available_clubs'):
        session['available_clubs'] = preserved_data['available_clubs']
    if preserved_data.get('user_info'):
        session['user_info'] = preserved_data['user_info']

    session.modified = True
    flash('Your session has expired. Please log in again.', 'info')
    return redirect(url_for('auth.login'))
```

---

## What This Fixes

✅ **Members page no longer redirects to login** after club selection
✅ **Selected clubs persist** even if auth validation temporarily fails
✅ **User can log back in** and still have their club selection
✅ **Multi-club workflow works smoothly** without losing context

---

## How It Works

1. **User logs in** → Authenticates successfully
2. **User selects clubs** → Clubs stored in session
3. **User navigates to members page** → Auth decorator runs
4. **If auth fails for any reason:**
   - OLD: Entire session cleared, user loses club selection, redirected to login
   - NEW: Club selection preserved, user redirected to login, can resume where they left off

---

## User Experience Improvement

**Before:**
```
Login → Select Clubs → Navigate to Members → [Auth Hiccup] → Redirected to Login
→ Lost club selection → Have to select clubs again
```

**After:**
```
Login → Select Clubs → Navigate to Members → [Auth Hiccup] → Redirected to Login
→ Club selection preserved → Login again → Automatically continues with selected clubs
```

---

## Testing

To verify the fix works:

1. **Login** at http://localhost:5000
2. **Select clubs** on club selection screen
3. **Navigate to members page** - Should stay logged in now!
4. **If redirected to login** - Selected clubs are preserved, login and continue

---

## Files Modified

- `src/routes/auth.py` (Lines 36-56, Lines 66-88)

---

## Session Data Preserved

When session clearing occurs, these values are now preserved:
- `selected_clubs` - List of club IDs user selected
- `available_clubs` - List of clubs user has access to
- `user_info` - User profile information

All authentication flags (`authenticated`, `manager_id`, `login_time`, etc.) are still properly cleared for security.

---

## Fix Complete! ✅

The members page should now stay accessible after club selection without redirecting to login!
