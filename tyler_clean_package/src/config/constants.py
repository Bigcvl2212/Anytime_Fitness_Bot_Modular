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