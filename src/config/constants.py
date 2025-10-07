#!/usr/bin/env python3
"""
Production Constants Configuration
"""

# Google Cloud Project Configuration
GCP_PROJECT_ID = "round-device-460522-g8"

# ClubOS API Configuration
CLUBOS_LOGIN_URL = "https://portal.clubos.com/login"
CLUBOS_CALENDAR_URL = "https://portal.clubos.com/calendar"
CLUBOS_BASE_URL = "https://portal.clubos.com"

# Club Configuration
CLUB_ID = "1156"  # Anytime Fitness Club ID

# Google Secret Manager Secret Names
CLUBOS_USERNAME_SECRET = "clubos-username"
CLUBOS_PASSWORD_SECRET = "clubos-password"
CLUBHUB_EMAIL_SECRET = "clubhub-email"
CLUBHUB_PASSWORD_SECRET = "clubhub-password"

# Database Configuration
DATABASE_URL_SECRET = "database-url"
POSTGRES_HOST = "34.31.91.96"
POSTGRES_PORT = 5432
POSTGRES_DB = "gym_bot"

# Session Configuration
SESSION_TIMEOUT = 3600  # 1 hour in seconds

# API Rate Limiting
DEFAULT_RATE_LIMIT = "100/hour"
AUTOMATION_RATE_LIMIT = "1000/hour"

# Training Session Configuration
TRAINING_SESSION_DURATION = 30  # minutes
STANDARD_MONTHLY_RATE = 39.50  # dollars
LATE_FEE_RATE = 19.50  # dollars per missed payment

# Message Configuration
MAX_MESSAGE_LENGTH = 500
MESSAGE_RETENTION_DAYS = 30

# Cache Configuration
CACHE_TTL = 300  # 5 minutes in seconds

# ClubOS Dashboard URLs
CLUBOS_DASHBOARD_URL = "https://anytime.club-os.com/action/Dashboard/view"
CLUBOS_MESSAGES_URL = "https://anytime.club-os.com/ajax/messages/history"

# Message Configuration
TEXT_MESSAGE_CHARACTER_LIMIT = 500

# Staff Configuration
NOTE_AUTHOR_NAME = "Gym Bot"
STAFF_NAMES = ["j.mayo", "mayo", "gym bot", "staff"]

# Request Limits
MAX_REQUEST_SIZE_BYTES = 10 * 1024 * 1024  # 10MB maximum request size
MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024  # 50MB for file uploads

# Rate Limiting (Additional)
RATE_LIMIT_WINDOW_SECONDS = 60  # Time window for rate limiting
MAX_REQUESTS_PER_WINDOW = 100  # Maximum requests per window
SUSPICIOUS_REQUEST_LIMIT = 10  # Lower limit for suspicious requests

# Database (Additional)
DATABASE_TIMEOUT_SECONDS = 30  # Database connection timeout
MAX_RETRY_ATTEMPTS = 3  # Maximum retry attempts for failed operations
CONNECTION_POOL_SIZE = 10  # Database connection pool size

# Caching (Additional)
PERFORMANCE_CACHE_SIZE = 1000  # Maximum cache entries
FUNDING_CACHE_TTL = 3600  # 1 hour for funding cache

# Sync Intervals
SYNC_INTERVAL_SECONDS = 3600  # 1 hour between full syncs
QUICK_SYNC_INTERVAL = 300  # 5 minutes for quick syncs
HEALTH_CHECK_INTERVAL = 180  # 3 minutes for health checks

# Access Control
LOCK_CHECK_INTERVAL = 1800  # 30 minutes between lock checks
UNLOCK_CHECK_INTERVAL = 180  # 3 minutes between unlock checks
ACCESS_MONITOR_SLEEP = 15  # Seconds between monitoring cycles

# Pagination
DEFAULT_PAGE_SIZE = 50  # Default items per page
MAX_PAGE_SIZE = 1000  # Maximum items per page

# Campaign Settings
CAMPAIGN_BATCH_SIZE = 50  # Messages per batch in campaigns
CAMPAIGN_DELAY_SECONDS = 2  # Delay between batches

# AI Service
AI_MAX_TOKENS = 4000  # Maximum tokens for AI responses
AI_TEMPERATURE = 0.7  # AI response temperature
AI_REQUEST_TIMEOUT = 30  # AI request timeout seconds
MIN_AI_REQUEST_INTERVAL = 1.0  # Minimum seconds between AI requests
DAILY_AI_LIMIT = 1000  # Daily AI request limit

# Session Management (Additional)
ADMIN_SESSION_TIMEOUT = 480  # 8 hours for admin sessions (minutes)
MAX_LOGIN_ATTEMPTS = 5  # Maximum failed login attempts
LOCKOUT_DURATION_MINUTES = 30  # Account lockout duration

# API Timeouts
CLUBOS_API_TIMEOUT = 30  # ClubOS API timeout seconds
SQUARE_API_TIMEOUT = 20  # Square API timeout seconds
DEFAULT_HTTP_TIMEOUT = 15  # Default HTTP request timeout

# Security
MIN_PASSWORD_LENGTH = 12  # Minimum password length
MIN_SECRET_KEY_LENGTH = 32  # Minimum Flask secret key length
PASSWORD_HASH_ROUNDS = 12  # BCrypt hash rounds

# ClubOS Specific (Additional)
CLUBOS_BATCH_SIZE = 50  # Members per ClubOS batch request
CLUBOS_RATE_LIMIT_DELAY = 1  # Delay between ClubOS requests

# Performance Monitoring
SLOW_QUERY_THRESHOLD = 1.0  # Log queries slower than 1 second
SLOW_REQUEST_THRESHOLD = 5.0  # Log requests slower than 5 seconds