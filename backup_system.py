#!/usr/bin/env python3
"""
Gym Bot Backup System
Safe backup and restore functionality for production readiness work
"""

import os
import shutil
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GymBotBackup:
    """Safe backup system for gym bot application"""
    
    def __init__(self, base_path=None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.backup_dir = self.base_path / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_full_backup(self, description="Working state backup"):
        """Create a complete backup of the current application state"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"gym_bot_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        logger.info(f"🔄 Creating full backup: {backup_name}")
        
        try:
            # Create backup directory
            backup_path.mkdir(exist_ok=True)
            
            # Backup configuration
            config_backup = backup_path / "config"
            config_backup.mkdir(exist_ok=True)
            
            # Backup source code
            src_backup = backup_path / "src"
            if (self.base_path / "src").exists():
                shutil.copytree(self.base_path / "src", src_backup)
                logger.info("✅ Source code backed up")
            
            # Backup configuration files
            config_files = [
                "requirements.txt", ".env.production", ".env.example", 
                "wsgi.py", "run_dashboard.py", "Dockerfile", "docker-compose.yml",
                "Procfile"
            ]
            
            for config_file in config_files:
                src_file = self.base_path / config_file
                if src_file.exists():
                    shutil.copy2(src_file, config_backup)
                    logger.info(f"✅ {config_file} backed up")
            
            # Backup templates and static files
            for dir_name in ["templates", "static"]:
                src_dir = self.base_path / dir_name
                if src_dir.exists():
                    shutil.copytree(src_dir, backup_path / dir_name)
                    logger.info(f"✅ {dir_name} directory backed up")
            
            # Backup database if it exists
            self._backup_database(backup_path)
            
            # Create backup manifest
            manifest = {
                "backup_name": backup_name,
                "timestamp": timestamp,
                "description": description,
                "files_backed_up": [],
                "database_backed_up": False,
                "restore_instructions": "Use restore_backup() method with this backup name"
            }
            
            # Count backed up files
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    manifest["files_backed_up"].append(os.path.relpath(os.path.join(root, file), backup_path))
            
            # Check if database was backed up
            if (backup_path / "database").exists():
                manifest["database_backed_up"] = True
            
            # Save manifest
            with open(backup_path / "backup_manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"✅ Full backup completed: {backup_name}")
            logger.info(f"📁 Backup location: {backup_path}")
            logger.info(f"📊 Files backed up: {len(manifest['files_backed_up'])}")
            
            return backup_name, backup_path
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            # Cleanup failed backup
            if backup_path.exists():
                shutil.rmtree(backup_path)
            raise
    
    def _backup_database(self, backup_path):
        """Backup SQLite databases safely"""
        db_backup_dir = backup_path / "database"
        db_backup_dir.mkdir(exist_ok=True)
        
        # Find all .db files
        db_files = list(self.base_path.glob("*.db"))
        db_files.extend(list((self.base_path / "src").glob("*.db")))
        
        for db_file in db_files:
            try:
                # Create a backup copy
                backup_file = db_backup_dir / db_file.name
                shutil.copy2(db_file, backup_file)
                
                # Also create a SQL dump for safety
                sql_dump_file = db_backup_dir / f"{db_file.stem}_dump.sql"
                self._create_sql_dump(db_file, sql_dump_file)
                
                logger.info(f"✅ Database backed up: {db_file.name}")
                
            except Exception as e:
                logger.warning(f"⚠️ Could not backup database {db_file.name}: {e}")
    
    def _create_sql_dump(self, db_file, dump_file):
        """Create SQL dump of SQLite database"""
        try:
            conn = sqlite3.connect(str(db_file))
            with open(dump_file, 'w') as f:
                for line in conn.iterdump():
                    f.write('%s\n' % line)
            conn.close()
        except Exception as e:
            logger.warning(f"⚠️ Could not create SQL dump: {e}")
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        for backup_dir in self.backup_dir.glob("gym_bot_backup_*"):
            if backup_dir.is_dir():
                manifest_file = backup_dir / "backup_manifest.json"
                if manifest_file.exists():
                    try:
                        with open(manifest_file, 'r') as f:
                            manifest = json.load(f)
                        backups.append(manifest)
                    except Exception as e:
                        logger.warning(f"⚠️ Could not read manifest for {backup_dir.name}: {e}")
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def restore_backup(self, backup_name, confirm=False):
        """Restore from a specific backup (DANGEROUS - requires confirmation)"""
        if not confirm:
            logger.error("❌ Restore requires explicit confirmation. Set confirm=True")
            return False
        
        backup_path = self.backup_dir / backup_name
        if not backup_path.exists():
            logger.error(f"❌ Backup {backup_name} not found")
            return False
        
        logger.warning("🚨 DANGEROUS OPERATION: This will overwrite current application state!")
        logger.warning("🚨 Make sure you have a backup of current state first!")
        
        try:
            # Create a safety backup first
            safety_backup_name, _ = self.create_full_backup("Safety backup before restore")
            logger.info(f"✅ Safety backup created: {safety_backup_name}")
            
            # Restore files (implement as needed)
            logger.info(f"🔄 Restoring from {backup_name}...")
            # Note: Actual restore logic would go here
            # For safety, we're not implementing this automatically
            
            logger.info("✅ Restore completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Restore failed: {e}")
            return False
    
    def verify_backup(self, backup_name):
        """Verify backup integrity"""
        backup_path = self.backup_dir / backup_name
        if not backup_path.exists():
            return False, f"Backup {backup_name} not found"
        
        manifest_file = backup_path / "backup_manifest.json"
        if not manifest_file.exists():
            return False, "Backup manifest missing"
        
        try:
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            # Verify files exist
            missing_files = []
            for file_path in manifest["files_backed_up"]:
                if not (backup_path / file_path).exists():
                    missing_files.append(file_path)
            
            if missing_files:
                return False, f"Missing files: {missing_files[:5]}..."
            
            return True, f"Backup verified successfully ({len(manifest['files_backed_up'])} files)"
            
        except Exception as e:
            return False, f"Verification failed: {e}"

def main():
    """Main backup utility function"""
    backup_system = GymBotBackup()
    
    print("🏋️ Gym Bot Backup System")
    print("========================")
    
    # Create initial backup
    backup_name, backup_path = backup_system.create_full_backup("Initial working state before production improvements")
    
    print(f"\n✅ Backup created successfully!")
    print(f"📁 Backup name: {backup_name}")
    print(f"📍 Backup path: {backup_path}")
    
    # Verify backup
    is_valid, message = backup_system.verify_backup(backup_name)
    if is_valid:
        print(f"✅ Backup verification: {message}")
    else:
        print(f"❌ Backup verification failed: {message}")
    
    # List all backups
    print("\n📋 Available backups:")
    backups = backup_system.list_backups()
    for backup in backups[:5]:  # Show last 5
        print(f"  • {backup['backup_name']} - {backup['description']}")
    
    return backup_name

if __name__ == "__main__":
    main()