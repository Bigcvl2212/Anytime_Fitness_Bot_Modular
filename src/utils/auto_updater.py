#!/usr/bin/env python3
"""
Auto-Updater for Gym Bot
Downloads and applies updates from GitHub without full reinstall
"""

import os
import sys
import json
import shutil
import logging
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Tuple
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

# GitHub repo info
GITHUB_OWNER = "Bigcvl2212"
GITHUB_REPO = "Anytime_Fitness_Bot_Modular"
GITHUB_BRANCH = "main"

# Files/folders to update (relative paths)
UPDATABLE_PATHS = [
    "src/",
    "templates/",
    "static/",
    "VERSION",
    "run_dashboard.py",
]

# Files to NEVER overwrite (user data)
PROTECTED_PATHS = [
    ".env",
    "gym_bot.db",
    "logs/",
    "backups/",
    "config/clubhub_credentials.py",
    "config/clubhub_credentials_clean.py",
]


class AutoUpdater:
    """Handles automatic updates from GitHub"""
    
    def __init__(self, app_dir: Optional[Path] = None):
        """Initialize the updater
        
        Args:
            app_dir: Application directory. If None, auto-detect.
        """
        if app_dir:
            self.app_dir = Path(app_dir)
        elif getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle - use user's AppData for updates
            self.app_dir = Path.home() / 'AppData' / 'Local' / 'GymBot'
        else:
            # Running as script
            self.app_dir = Path(__file__).parent.parent.parent
        
        self.backup_dir = self.app_dir / 'backups' / 'updates'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.github_api_base = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        self.github_raw_base = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
    
    def get_local_version(self) -> str:
        """Get the current local version"""
        version_file = self.app_dir / 'VERSION'
        if version_file.exists():
            return version_file.read_text().strip()
        return "0.0.0"
    
    def get_remote_version(self) -> Optional[str]:
        """Get the latest version from GitHub"""
        try:
            url = f"{self.github_raw_base}/VERSION"
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.read().decode('utf-8').strip()
        except Exception as e:
            logger.error(f"Failed to get remote version: {e}")
            return None
    
    def check_for_updates(self) -> Tuple[bool, str, str]:
        """Check if updates are available
        
        Returns:
            Tuple of (update_available, local_version, remote_version)
        """
        local = self.get_local_version()
        remote = self.get_remote_version()
        
        if remote is None:
            return False, local, "unknown"
        
        # Parse versions
        try:
            local_parts = [int(x) for x in local.split('.')]
            remote_parts = [int(x) for x in remote.split('.')]
            
            # Compare versions
            update_available = remote_parts > local_parts
            return update_available, local, remote
        except ValueError:
            # If parsing fails, compare as strings
            return remote != local, local, remote
    
    def download_file(self, remote_path: str, local_path: Path) -> bool:
        """Download a single file from GitHub
        
        Args:
            remote_path: Path relative to repo root
            local_path: Local path to save to
            
        Returns:
            True if successful
        """
        try:
            url = f"{self.github_raw_base}/{remote_path}"
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read()
                local_path.write_bytes(content)
            
            logger.info(f"Downloaded: {remote_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download {remote_path}: {e}")
            return False
    
    def download_zip(self) -> Optional[Path]:
        """Download the entire repo as a ZIP file
        
        Returns:
            Path to downloaded ZIP or None if failed
        """
        try:
            url = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"
            
            # Download to temp file
            temp_dir = Path(tempfile.mkdtemp())
            zip_path = temp_dir / "update.zip"
            
            logger.info(f"Downloading update from {url}...")
            urllib.request.urlretrieve(url, zip_path)
            
            return zip_path
        except Exception as e:
            logger.error(f"Failed to download ZIP: {e}")
            return None
    
    def backup_current(self) -> Optional[Path]:
        """Backup current installation
        
        Returns:
            Path to backup or None if failed
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{timestamp}"
            backup_path.mkdir(parents=True, exist_ok=True)
            
            for update_path in UPDATABLE_PATHS:
                src = self.app_dir / update_path
                if src.exists():
                    dst = backup_path / update_path
                    if src.is_dir():
                        shutil.copytree(src, dst)
                    else:
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dst)
            
            logger.info(f"Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def apply_update(self, zip_path: Path) -> bool:
        """Apply update from ZIP file
        
        Args:
            zip_path: Path to downloaded ZIP
            
        Returns:
            True if successful
        """
        try:
            # Extract ZIP
            extract_dir = zip_path.parent / "extracted"
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_dir)
            
            # Find the repo folder (named like "Anytime_Fitness_Bot_Modular-main")
            repo_dirs = list(extract_dir.glob(f"{GITHUB_REPO}-*"))
            if not repo_dirs:
                logger.error("Could not find repo folder in ZIP")
                return False
            
            repo_dir = repo_dirs[0]
            
            # Copy updatable paths
            for update_path in UPDATABLE_PATHS:
                src = repo_dir / update_path
                dst = self.app_dir / update_path
                
                if not src.exists():
                    logger.warning(f"Source not found: {update_path}")
                    continue
                
                # Check if protected
                if any(update_path.startswith(p) for p in PROTECTED_PATHS):
                    logger.info(f"Skipping protected: {update_path}")
                    continue
                
                # Remove old and copy new
                if dst.exists():
                    if dst.is_dir():
                        shutil.rmtree(dst)
                    else:
                        dst.unlink()
                
                if src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                
                logger.info(f"Updated: {update_path}")
            
            # Cleanup
            shutil.rmtree(zip_path.parent)
            
            logger.info("Update applied successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply update: {e}")
            return False
    
    def rollback(self, backup_path: Path) -> bool:
        """Rollback to a previous backup
        
        Args:
            backup_path: Path to backup folder
            
        Returns:
            True if successful
        """
        try:
            for update_path in UPDATABLE_PATHS:
                src = backup_path / update_path
                dst = self.app_dir / update_path
                
                if not src.exists():
                    continue
                
                if dst.exists():
                    if dst.is_dir():
                        shutil.rmtree(dst)
                    else:
                        dst.unlink()
                
                if src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
            
            logger.info(f"Rolled back to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def perform_update(self, progress_callback=None) -> Tuple[bool, str]:
        """Perform a full update
        
        Args:
            progress_callback: Optional callback(message, percent) for progress
            
        Returns:
            Tuple of (success, message)
        """
        def report(msg, pct):
            logger.info(msg)
            if progress_callback:
                progress_callback(msg, pct)
        
        # Check for updates
        report("Checking for updates...", 10)
        update_available, local_ver, remote_ver = self.check_for_updates()
        
        if not update_available:
            return True, f"Already up to date (v{local_ver})"
        
        report(f"Update available: v{local_ver} → v{remote_ver}", 20)
        
        # Create backup
        report("Creating backup...", 30)
        backup_path = self.backup_current()
        if not backup_path:
            return False, "Failed to create backup"
        
        # Download update
        report("Downloading update...", 50)
        zip_path = self.download_zip()
        if not zip_path:
            return False, "Failed to download update"
        
        # Apply update
        report("Applying update...", 80)
        if not self.apply_update(zip_path):
            report("Update failed, rolling back...", 90)
            self.rollback(backup_path)
            return False, "Update failed, rolled back to previous version"
        
        report(f"Updated to v{remote_ver}!", 100)
        return True, f"Successfully updated to v{remote_ver}"


def check_for_updates() -> Tuple[bool, str, str]:
    """Convenience function to check for updates"""
    updater = AutoUpdater()
    return updater.check_for_updates()


def perform_update(progress_callback=None) -> Tuple[bool, str]:
    """Convenience function to perform update"""
    updater = AutoUpdater()
    return updater.perform_update(progress_callback)


if __name__ == '__main__':
    # Test the updater
    logging.basicConfig(level=logging.INFO)
    
    updater = AutoUpdater()
    
    print("Checking for updates...")
    available, local, remote = updater.check_for_updates()
    
    print(f"Local version: {local}")
    print(f"Remote version: {remote}")
    print(f"Update available: {available}")
    
    if available:
        response = input("Apply update? (y/n): ")
        if response.lower() == 'y':
            success, msg = updater.perform_update()
            print(msg)
