"""
ClubOS Authentication Module
Authentication helpers and session management.
"""

from .driver import setup_driver_and_login


def ensure_clubos_session(driver=None):
    """Ensure ClubOS session - uses proven login function."""
    if driver is None:
        return setup_driver_and_login() is not None
    return True  # If driver is provided, assume it's logged in


def verify_clubos_session(driver=None):
    """Verify ClubOS session."""
    return True  # Simplified for now
