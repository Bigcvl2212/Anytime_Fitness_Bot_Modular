#!/usr/bin/env python3
"""
ClubHub Authentication Service
Provides authentication with ClubHub API and returns JWT bearer tokens
"""

import logging
from typing import Optional
from ..api.clubhub_api_client import ClubHubAPIClient

logger = logging.getLogger(__name__)

class ClubHubAuth:
    """
    ClubHub authentication service that wraps the ClubHub API client
    """

    def __init__(self):
        """Initialize ClubHub authentication service"""
        self.api_client = ClubHubAPIClient()

    def authenticate(self, email: str, password: str) -> Optional[str]:
        """
        Authenticate with ClubHub and return the JWT bearer token

        Args:
            email: ClubHub email address
            password: ClubHub password

        Returns:
            JWT bearer token if successful, None otherwise
        """
        try:
            logger.info(f"🔐 Authenticating with ClubHub for {email}")

            # Authenticate using the API client
            success = self.api_client.authenticate(email, password)

            if not success:
                logger.warning(f"❌ ClubHub authentication failed for {email}")
                return None

            # Return the bearer token
            if self.api_client.auth_token:
                logger.info(f"✅ ClubHub authentication successful for {email}")
                return self.api_client.auth_token
            else:
                logger.warning(f"⚠️ ClubHub authentication succeeded but no token received for {email}")
                return None

        except Exception as e:
            logger.error(f"❌ ClubHub authentication error for {email}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
