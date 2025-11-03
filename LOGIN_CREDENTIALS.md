# Login Credentials - Anytime Fitness Dashboard

## Admin Accounts

### Account 1: J. Mayo (Your Personal Account)
```
Username: j.mayo
Password: admin123
Access Level: Super Admin
Manager ID: MGR001
```

### Account 2: Default Admin
```
Username: admin
Password: admin
Access Level: Super Admin
Manager ID: 8fbdf1fb901c0392
```

## Login Instructions

1. **Start the application:**
   ```bash
   python run_dashboard.py
   ```

2. **Open in browser:**
   ```
   http://localhost:5000/login
   ```

3. **Enter credentials:**
   - Use either account above
   - Both have full super admin access

## Security Notes

⚠️ **IMPORTANT:** These are development/default passwords.

**Recommended actions:**
1. Change your password after first login
2. Go to Settings → Account Settings
3. Use strong passwords for production

## Troubleshooting

**If login fails:**
1. Check username is exactly as shown (case-sensitive)
2. Check password is exactly as shown
3. Clear browser cookies/cache
4. Check terminal for error messages

**Password Reset (if needed):**
```python
python -c "
from werkzeug.security import generate_password_hash
import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

new_password = 'your_new_password'
password_hash = generate_password_hash(new_password)

cursor.execute('UPDATE admin_users SET password_hash = ? WHERE username = ?',
               (password_hash, 'j.mayo'))
conn.commit()
conn.close()
print('Password updated')
"
```

## Features Available

With super admin access, you have full control over:

- ✅ Member Management
- ✅ Prospect Tracking
- ✅ Training Client Management
- ✅ Messaging System
- ✅ Campaign Management
- ✅ Invoice Creation (Square Integration)
- ✅ Calendar & Scheduling
- ✅ AI Agent Configuration
- ✅ Workflow Automation
- ✅ System Settings
- ✅ User Management
- ✅ Admin Dashboard

## Support

If you encounter any issues, check the application logs in the terminal for detailed error messages.
