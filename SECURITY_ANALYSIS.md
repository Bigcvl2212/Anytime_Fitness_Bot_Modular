# Security Analysis & Recommendations

## Current Security Implementation

### Location: `src/main_app.py` lines 29-55

**Current Protections:**
1. ✅ Large request detection (>10MB)
2. ✅ Basic XSS pattern detection (`<script`, `javascript:`)
3. ✅ Basic SQL injection detection (`union select`, `drop table`, `insert into`, `delete from`)

## Security Gaps Identified

### 1. **Base64-Encoded Attacks** ❌
**Risk**: Attackers can encode malicious payloads in Base64 to bypass pattern matching.

**Example Attack:**
```python
# Base64 encoded: "<script>alert('XSS')</script>"
payload = "PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4="
```

**Recommendation**:
```python
import base64

def check_base64_attacks(value):
    """Detect Base64-encoded malicious content"""
    try:
        # Try to decode potential Base64
        decoded = base64.b64decode(value).decode('utf-8', errors='ignore')
        # Check decoded content for malicious patterns
        if '<script' in decoded.lower() or 'javascript:' in decoded.lower():
            return True
    except:
        pass
    return False
```

### 2. **Unicode Normalization Attacks** ❌
**Risk**: Unicode characters can be used to bypass filters (e.g., `＜script＞` instead of `<script>`).

**Example Attack:**
```python
# Fullwidth characters that render as normal characters
payload = "＜script＞alert('XSS')＜/script＞"
```

**Recommendation**:
```python
import unicodedata

def normalize_and_check(value):
    """Normalize Unicode and check for attacks"""
    # Convert fullwidth/halfwidth characters to normal
    normalized = unicodedata.normalize('NFKC', value)
    # Now check normalized string for patterns
    return normalized
```

### 3. **Path Traversal Attempts** ❌
**Risk**: Directory traversal can access files outside intended directories.

**Example Attack:**
```python
payload = "../../../../etc/passwd"
payload = "..\\..\\..\\windows\\system32\\config\\sam"
```

**Recommendation**:
```python
def check_path_traversal(value):
    """Detect path traversal attempts"""
    dangerous_patterns = [
        '../', '..\\',
        '%2e%2e%2f',  # URL encoded ../
        '%2e%2e/',
        '..%2f',
        '%252e%252e%252f',  # Double URL encoded
    ]
    normalized = value.lower()
    for pattern in dangerous_patterns:
        if pattern in normalized:
            return True
    return False
```

### 4. **Command Injection in Headers** ❌
**Risk**: HTTP headers can contain command injection payloads.

**Example Attack:**
```python
# User-Agent header with command injection
headers = {
    'User-Agent': 'Mozilla/5.0; $(whoami)',
    'X-Forwarded-For': '127.0.0.1; cat /etc/passwd'
}
```

**Recommendation**:
```python
def check_header_injection():
    """Validate HTTP headers for injection attempts"""
    suspicious_headers = ['User-Agent', 'X-Forwarded-For', 'Referer', 'X-Real-IP']
    cmd_patterns = ['$(', '`', '|', '&&', '||', ';', '\n', '\r']

    for header in suspicious_headers:
        value = request.headers.get(header, '')
        if any(pattern in value for pattern in cmd_patterns):
            logger.warning(f"Command injection attempt in header {header}: {value[:100]}")
            return True
    return False
```

### 5. **Rate Limiting per IP** ❌
**Risk**: No protection against brute force or DoS attacks from single IPs.

**Recommendation**:
```python
from collections import defaultdict
from datetime import datetime, timedelta

# In-memory rate limiter (use Redis for production)
request_counts = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
MAX_REQUESTS = 100  # per window
SUSPICIOUS_MAX = 10  # lower limit for suspicious patterns

def check_rate_limit(ip_address, is_suspicious=False):
    """Check if IP has exceeded rate limits"""
    now = datetime.now()
    window_start = now - timedelta(seconds=RATE_LIMIT_WINDOW)

    # Clean old requests
    request_counts[ip_address] = [
        req_time for req_time in request_counts[ip_address]
        if req_time > window_start
    ]

    # Add current request
    request_counts[ip_address].append(now)

    # Check limits
    limit = SUSPICIOUS_MAX if is_suspicious else MAX_REQUESTS
    if len(request_counts[ip_address]) > limit:
        logger.warning(f"Rate limit exceeded for {ip_address}: {len(request_counts[ip_address])} requests in {RATE_LIMIT_WINDOW}s")
        return True
    return False
```

### 6. **Additional Security Enhancements**

#### a) **LDAP Injection** ❌
```python
ldap_patterns = ['*', '(', ')', '&', '|', '!']
```

#### b) **XML External Entity (XXE) Attacks** ❌
```python
xxe_patterns = ['<!entity', '<!doctype', 'system "file://']
```

#### c) **Server-Side Template Injection (SSTI)** ❌
```python
ssti_patterns = ['{{', '<%', '{%', '#{']
```

#### d) **NoSQL Injection** ❌
```python
nosql_patterns = ['$ne', '$gt', '$where', '$regex']
```

## Recommended Enhanced Sanitization Function

### Complete Implementation: `src/main_app.py`

```python
import base64
import unicodedata
from collections import defaultdict
from datetime import datetime, timedelta

# Rate limiting storage
request_counts = defaultdict(list)
RATE_LIMIT_WINDOW = 60
MAX_REQUESTS = 100
SUSPICIOUS_MAX = 10

def add_request_sanitization(app):
    """Enhanced request sanitization middleware"""

    @app.before_request
    def sanitize_request():
        """Comprehensive request sanitization"""
        ip_address = request.remote_addr
        is_suspicious = False

        # 1. Large request check
        content_length = request.content_length or 0
        if content_length > 10 * 1024 * 1024:  # 10MB
            logger.warning(f"⚠️ Large request from {ip_address}: {content_length} bytes")
            is_suspicious = True

        # 2. Command injection in headers
        if check_header_injection():
            is_suspicious = True

        # 3. Validate request data
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.form:
                for key, value in request.form.items():
                    if isinstance(value, str):
                        # Unicode normalization
                        normalized_value = unicodedata.normalize('NFKC', value)

                        # XSS detection (including encoded)
                        if check_xss(normalized_value):
                            logger.warning(f"🚨 XSS attempt from {ip_address}: {key}={normalized_value[:100]}")
                            is_suspicious = True

                        # SQL injection
                        if check_sql_injection(normalized_value):
                            logger.warning(f"🚨 SQL injection from {ip_address}: {key}={normalized_value[:100]}")
                            is_suspicious = True

                        # Path traversal
                        if check_path_traversal(normalized_value):
                            logger.warning(f"🚨 Path traversal from {ip_address}: {key}={normalized_value[:100]}")
                            is_suspicious = True

                        # Base64 encoded attacks
                        if check_base64_attacks(value):
                            logger.warning(f"🚨 Base64 encoded attack from {ip_address}: {key}")
                            is_suspicious = True

                        # Template injection
                        if check_template_injection(normalized_value):
                            logger.warning(f"🚨 Template injection from {ip_address}: {key}={normalized_value[:100]}")
                            is_suspicious = True

        # 4. Rate limiting (stricter for suspicious requests)
        if check_rate_limit(ip_address, is_suspicious):
            from flask import abort
            abort(429)  # Too Many Requests

    logger.info("✅ Enhanced request sanitization middleware configured")

def check_xss(value):
    """Detect XSS patterns"""
    xss_patterns = [
        '<script', '</script', 'javascript:', 'onerror=',
        'onload=', 'onclick=', '<iframe', 'eval(',
        'expression(', '<object', '<embed'
    ]
    value_lower = value.lower()
    return any(pattern in value_lower for pattern in xss_patterns)

def check_sql_injection(value):
    """Detect SQL injection patterns"""
    sql_patterns = [
        'union select', 'drop table', 'insert into',
        'delete from', '1=1', '1\'=\'1', 'or 1=1',
        'exec(', 'execute(', 'xp_cmdshell', '--', ';--'
    ]
    value_lower = value.lower()
    return any(pattern in value_lower for pattern in sql_patterns)

def check_path_traversal(value):
    """Detect path traversal"""
    dangerous_patterns = [
        '../', '..\\', '%2e%2e%2f', '%2e%2e/',
        '..%2f', '%252e%252e%252f', '....',
        'file://', '/etc/', 'c:\\', 'windows\\system32'
    ]
    value_lower = value.lower()
    return any(pattern in value_lower for pattern in dangerous_patterns)

def check_base64_attacks(value):
    """Detect Base64-encoded malicious content"""
    try:
        if len(value) > 20 and len(value) % 4 == 0:  # Likely Base64
            decoded = base64.b64decode(value, validate=True).decode('utf-8', errors='ignore')
            if check_xss(decoded) or check_sql_injection(decoded):
                return True
    except:
        pass
    return False

def check_template_injection(value):
    """Detect template injection (SSTI)"""
    ssti_patterns = ['{{', '}}', '{%', '%}', '<%', '%>', '#{', '}', '${']
    return any(pattern in value for pattern in ssti_patterns)

def check_header_injection():
    """Validate HTTP headers"""
    suspicious_headers = ['User-Agent', 'X-Forwarded-For', 'Referer', 'X-Real-IP']
    cmd_patterns = ['$(', '`', '|', '&&', '||', ';', '\n', '\r', '\x00']

    for header in suspicious_headers:
        value = request.headers.get(header, '')
        if any(pattern in value for pattern in cmd_patterns):
            logger.warning(f"🚨 Command injection in header {header}: {value[:100]}")
            return True
    return False

def check_rate_limit(ip_address, is_suspicious=False):
    """Check rate limits"""
    now = datetime.now()
    window_start = now - timedelta(seconds=RATE_LIMIT_WINDOW)

    # Clean old requests
    request_counts[ip_address] = [
        req_time for req_time in request_counts[ip_address]
        if req_time > window_start
    ]

    # Add current request
    request_counts[ip_address].append(now)

    # Check limits
    limit = SUSPICIOUS_MAX if is_suspicious else MAX_REQUESTS
    if len(request_counts[ip_address]) > limit:
        logger.warning(f"🚨 Rate limit exceeded for {ip_address}: {len(request_counts[ip_address])} requests")
        return True
    return False
```

## Secrets Management Review

### Location: `src/main_app.py` lines 163-171

**Current Issue**: Secrets are retrieved but not validated for emptiness before use.

**Recommendation**:
```python
# Example from main_app.py
secrets = app.secrets_manager.get_all_secrets()

# BEFORE (vulnerable):
app.config['SECRET_KEY'] = secrets.get('flask-secret-key')

# AFTER (secure):
flask_secret = secrets.get('flask-secret-key')
if not flask_secret or len(flask_secret) < 32:
    raise ValueError("Flask secret key must be at least 32 characters")
app.config['SECRET_KEY'] = flask_secret

# Validate all critical secrets
required_secrets = {
    'flask-secret-key': 32,
    'database-password': 8,
    'api-key': 16
}

for secret_name, min_length in required_secrets.items():
    secret_value = secrets.get(secret_name)
    if not secret_value or len(secret_value) < min_length:
        raise ValueError(f"Secret '{secret_name}' must be at least {min_length} characters")
```

## Implementation Priority

### High Priority (Implement Now)
1. ✅ Path traversal detection
2. ✅ Command injection in headers
3. ✅ Rate limiting per IP
4. ✅ Secrets validation

### Medium Priority (Next Sprint)
5. ✅ Base64 attack detection
6. ✅ Unicode normalization
7. ✅ Template injection detection

### Low Priority (Future Enhancement)
8. Web Application Firewall (WAF) integration
9. Security headers (CSP, HSTS, X-Frame-Options)
10. Automated security scanning in CI/CD

## Additional Recommendations

1. **Input Validation Decorator**: Create a `@validate_input` decorator for routes
2. **Database Security**: Add comments explaining parameterized queries
3. **Logging**: Log all security events to separate security log file
4. **Monitoring**: Set up alerts for repeated security violations
5. **Testing**: Create security-specific unit tests

## Conclusion

The current sanitization provides basic protection but has significant gaps. Implementing the recommended enhancements will provide defense-in-depth against:
- Encoded attacks (Base64, Unicode)
- Path traversal
- Command injection
- Brute force/DoS via rate limiting
- Template injection attacks

**Estimated Implementation Time**: 4-6 hours for complete security hardening.
