"""
Core package initialization
"""

from .driver import setup_driver_and_login, login_to_clubos
from .authentication import ensure_clubos_session, verify_clubos_session
