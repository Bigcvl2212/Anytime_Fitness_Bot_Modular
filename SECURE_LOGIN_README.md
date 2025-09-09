# Secure Manager Login System

## 🔐 Overview

This secure login system replaces hardcoded credentials with encrypted storage in Google Cloud Secret Manager, providing enterprise-level security for the Anytime Fitness Dashboard Bot.

## 🎯 Key Features

### Security Features
- ✅ **Encrypted Credential Storage**: All credentials are encrypted and stored in Google Cloud Secret Manager
- ✅ **No Plain Text Passwords**: Passwords are never stored in code or databases
- ✅ **Secure Session Management**: 8-hour session timeout with automatic invalidation
- ✅ **CSRF Protection**: Security headers and CSRF protection on all forms
- ✅ **Input Validation**: Comprehensive validation and sanitization of all inputs
- ✅ **API Endpoint Protection**: All API endpoints require authentication
- ✅ **HTTPS/TLS Encryption**: All communications encrypted in transit

### User Experience Features  
- ✅ **Professional UI**: Clean, modern interface with responsive design
- ✅ **Manager Authentication**: Unique manager ID generation based on credentials
- ✅ **Backward Compatibility**: Drop-in replacement for existing credential access
- ✅ **Error Handling**: Comprehensive error messages and graceful degradation
- ✅ **Session Status**: Real-time session validation and status updates

## 🚀 Quick Start

### 1. Run the Demo
```bash
cd /home/runner/work/Anytime_Fitness_Bot_Modular/Anytime_Fitness_Bot_Modular
python run_secure_demo.py
```

### 2. Register Manager Credentials
1. Visit http://localhost:5000
2. Click "Register your credentials securely"
3. Enter your ClubOS and ClubHub credentials
4. Credentials are encrypted and stored securely

### 3. Login and Access Dashboard
1. Login with the same credentials
2. Access the secure dashboard with encrypted credential access
3. Test API endpoints and credential retrieval

## 📋 File Structure

```
services/authentication/
├── __init__.py                    # Package initialization
├── secure_secrets_manager.py     # Google Secret Manager integration
├── secure_auth_service.py        # Authentication and session management
└── secure_credential_service.py  # Backward compatibility service

templates/
├── login.html                     # Secure login page
├── register.html                  # Manager registration page
├── secure_dashboard.html          # Main dashboard
├── settings.html                  # Credential management
└── error.html                     # Error pages

secure_dashboard_app.py            # Main Flask application
run_secure_demo.py                 # Demo runner
secure_integration_examples.py    # Integration examples
```

## 🔧 Integration with Existing Services

### Before (Insecure)
```python
from config.clubhub_credentials import CLUBOS_USERNAME, CLUBOS_PASSWORD

def some_api_call():
    # Hardcoded credentials - INSECURE
    return api.login(CLUBOS_USERNAME, CLUBOS_PASSWORD)
```

### After (Secure)
```python
from services.authentication.secure_credential_service import get_clubos_credentials, is_authenticated

def some_api_call():
    # Check authentication first
    if not is_authenticated():
        return {"error": "Please login first"}
    
    # Get credentials securely
    username, password = get_clubos_credentials()
    if username and password:
        return api.login(username, password)
    else:
        return {"error": "Credentials not available"}
```

## 🔑 API Endpoints

### Authentication Endpoints
- `POST /login` - Manager login
- `POST /register` - Manager registration  
- `GET /logout` - End session
- `GET /dashboard` - Main dashboard (requires auth)
- `GET /settings` - Credential management (requires auth)

### API Endpoints
- `GET /api/credentials/<manager_id>` - Get manager credentials (requires auth)
- `GET /api/session` - Get session information
- `GET /health` - Health check

## 🛡️ Security Implementation

### Credential Storage
- Credentials are encrypted using Google Cloud Secret Manager
- Each manager gets a unique ID generated from username/email hash
- Passwords are never stored in plain text anywhere
- Legacy secret access is supported for backward compatibility

### Session Management
- Flask-Session with filesystem storage
- 8-hour session timeout
- Automatic session validation on each request
- Session tokens are cryptographically secure

### API Security
- All protected routes require active authentication
- CSRF protection on all forms
- Security headers (X-Frame-Options, CSP, etc.)
- Input validation and sanitization

## 📊 Monitoring and Logging

The system provides comprehensive logging:
- Authentication attempts (success/failure)
- Credential access attempts
- Session management events
- Security violations
- Error conditions

Example log output:
```
2024-01-15 10:30:25 - INFO - ✅ Manager abc123 logged in successfully from 192.168.1.100
2024-01-15 10:30:45 - INFO - ✅ Retrieved credentials for authenticated manager abc123
2024-01-15 10:35:12 - WARNING - ❌ Failed login attempt from 192.168.1.200: Invalid credentials
```

## 🔄 Migration Guide

### Step 1: Update Imports
Replace hardcoded credential imports with secure credential service:
```python
# OLD
from config.clubhub_credentials import CLUBOS_USERNAME, CLUBOS_PASSWORD

# NEW  
from services.authentication.secure_credential_service import get_clubos_credentials
```

### Step 2: Add Authentication Checks
```python
from services.authentication.secure_credential_service import is_authenticated

def protected_function():
    if not is_authenticated():
        return redirect('/login')
    # ... rest of function
```

### Step 3: Update Credential Access
```python
# OLD
username = CLUBOS_USERNAME
password = CLUBOS_PASSWORD

# NEW
username, password = get_clubos_credentials()
if not username or not password:
    return {"error": "Please login to access this feature"}
```

## 🏗️ Production Deployment

### Environment Variables
```bash
export GCP_PROJECT_ID="your-gcp-project-id"
export FLASK_SECRET_KEY="your-secure-secret-key"
export FLASK_ENV="production"
```

### Google Cloud Setup
1. Enable Secret Manager API
2. Set up Application Default Credentials
3. Grant necessary IAM permissions
4. Configure service account access

### Security Checklist
- [ ] HTTPS enabled with valid SSL certificate
- [ ] Firewall rules configured properly
- [ ] Regular security audits scheduled
- [ ] Backup and recovery procedures in place
- [ ] Monitoring and alerting configured

## 🧪 Testing

Run the demo to test all features:
```bash
python run_secure_demo.py
```

Check integration examples:
```bash
python secure_integration_examples.py --info
```

## 📞 Support

For issues or questions:
1. Check the logs for error details
2. Verify GCP credentials and permissions
3. Test with the demo environment first
4. Review the integration examples

## 🔒 Security Notes

- Never commit secrets or credentials to version control
- Use strong passwords and enable 2FA where possible
- Regularly rotate credentials and session keys
- Monitor access logs for suspicious activity
- Keep dependencies up to date with security patches