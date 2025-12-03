#!/usr/bin/env python3
"""
Environment Setup Module

This module handles loading environment variables from .env file
and ensures secure credential management.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def _get_user_config_env_path() -> Optional[Path]:
    """Return user-specific config directory (aligned with launcher/wizard)"""
    override = os.environ.get('GYMBOT_CONFIG_DIR')
    if override:
        return Path(override).expanduser() / '.env'

    if sys.platform == 'win32':
        local_appdata = os.environ.get('LOCALAPPDATA')
        if local_appdata:
            return Path(local_appdata) / 'GymBot' / '.env'
    elif sys.platform == 'darwin':
        return Path.home() / 'Library' / 'Application Support' / 'GymBot' / '.env'
    else:
        xdg_home = os.environ.get('XDG_CONFIG_HOME')
        base = Path(xdg_home) if xdg_home else Path.home() / '.config'
        return base / 'gymbot' / '.env'

    return None


def load_environment_variables() -> bool:
    """
    Load environment variables from .env file if present
    
    Returns:
        bool: True if .env file was loaded, False otherwise
    """
    try:
        # Try to import python-dotenv
        from dotenv import load_dotenv
        
        project_root = Path(__file__).parent.parent.parent
        default_env = project_root / '.env'

        env_candidates: list[Path] = [default_env]

        meipass = getattr(sys, '_MEIPASS', None)
        if meipass:
            env_candidates.append(Path(meipass) / '.env')

        if getattr(sys, 'frozen', False):
            env_candidates.append(Path(sys.executable).resolve().parent / '.env')

        user_env = _get_user_config_env_path()
        if user_env:
            env_candidates.append(user_env)

        custom_env = os.environ.get('GYMBOT_ENV_FILE')
        if custom_env:
            env_candidates.append(Path(custom_env).expanduser())

        loaded_any = False
        seen: set[str] = set()

        for env_path in env_candidates:
            if not env_path:
                continue

            env_key = str(env_path)
            if env_key in seen:
                continue
            seen.add(env_key)

            if env_path.exists():
                load_dotenv(env_path, override=True)
                logger.info(f"✅ Environment variables loaded from {env_path}")
                loaded_any = True

        if not loaded_any:
            logger.info("ℹ️ No .env file found - using system environment variables")

        return loaded_any
            
    except ImportError:
        logger.warning("⚠️ python-dotenv not installed. Install it with: pip install python-dotenv")
        logger.info("ℹ️ Using system environment variables only")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to load environment variables: {e}")
        return False

def validate_environment_setup() -> tuple[bool, list[str]]:
    """
    Validate that required environment variables are set
    
    Returns:
        tuple: (is_valid, missing_variables)
    """
    required_vars = [
        'FLASK_SECRET_KEY',
        'GCP_PROJECT_ID'
    ]
    
    optional_vars = [
        'FLASK_ENV',
        'LOG_LEVEL'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    # Log status of optional variables
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"✅ {var} = {value}")
        else:
            logger.info(f"ℹ️ {var} not set (using default)")
    
    return len(missing) == 0, missing

def get_flask_secret_key() -> str:
    """
    Get Flask secret key from environment with fallback
    
    Returns:
        str: Flask secret key
    """
    # Try FLASK_SECRET_KEY first
    secret_key = os.getenv('FLASK_SECRET_KEY')
    if secret_key and secret_key not in ['dev-secret-key-change-in-production', 'your-super-secret-key-change-in-production']:
        return secret_key
    
    # Try SECRET_KEY as fallback
    secret_key = os.getenv('SECRET_KEY')
    if secret_key and secret_key not in ['replace_me_with_a_real_secret', 'dev-secret-key-change-in-production']:
        return secret_key
    
    # Generate secure key if none found
    import secrets
    generated_key = secrets.token_urlsafe(32)
    logger.warning("⚠️ No secure secret key found. Generated temporary key. Set FLASK_SECRET_KEY environment variable.")
    return generated_key

def is_production_environment() -> bool:
    """
    Check if running in production mode
    
    Returns:
        bool: True if production
    """
    flask_env = os.getenv('FLASK_ENV', 'development').lower()
    return flask_env == 'production'

def setup_logging_from_env() -> dict:
    """
    Setup logging configuration from environment variables
    
    Returns:
        dict: Logging configuration
    """
    return {
        'level': os.getenv('LOG_LEVEL', 'INFO').upper(),
        'file': os.getenv('LOG_FILE', 'logs/dashboard.log'),
        'max_bytes': int(os.getenv('LOG_MAX_BYTES', '2000000')),
        'backup_count': int(os.getenv('LOG_BACKUP_COUNT', '3'))
    }

# Auto-load environment variables when module is imported
if __name__ != '__main__':
    load_environment_variables()