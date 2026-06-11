# -*- coding: utf-8 -*-
"""
Application paths management
All user data stored in AppData/Local/B2BManagement/
"""
import os
import sys
from pathlib import Path


class AppPaths:
    """Manage application paths - never store user data in Program Files"""
    
    def __init__(self, app_name: str = "B2BManagement"):
        self.app_name = app_name
        
        # Base directories
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            self.app_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            self.app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # User data directory (AppData/Local)
        self.local_app_data = os.path.join(
            os.getenv('LOCALAPPDATA', os.path.expanduser('~')),
            app_name
        )
        
        # Create all necessary directories
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create all required directories"""
        directories = [
            self.local_app_data,
            self.db_dir,
            self.backup_dir,
            self.exports_dir,
            self.imports_dir,
            self.uploads_dir,
            self.logs_dir,
            self.updates_dir,
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @property
    def db_dir(self) -> str:
        """Database directory"""
        return os.path.join(self.local_app_data, 'data')
    
    @property
    def database_path(self) -> str:
        """Main database file"""
        return os.path.join(self.db_dir, 'app.db')
    
    @property
    def config_path(self) -> str:
        """Configuration file"""
        return os.path.join(self.local_app_data, 'config.json')
    
    @property
    def license_path(self) -> str:
        """License file"""
        return os.path.join(self.local_app_data, 'license.json')
    
    @property
    def backup_dir(self) -> str:
        """Database backups"""
        return os.path.join(self.local_app_data, 'backup')
    
    @property
    def exports_dir(self) -> str:
        """Exported files"""
        return os.path.join(self.local_app_data, 'exports')
    
    @property
    def imports_dir(self) -> str:
        """Imported files"""
        return os.path.join(self.local_app_data, 'imports')
    
    @property
    def uploads_dir(self) -> str:
        """Uploaded files"""
        return os.path.join(self.local_app_data, 'uploads')
    
    @property
    def logs_dir(self) -> str:
        """Application logs"""
        return os.path.join(self.local_app_data, 'logs')
    
    @property
    def updates_dir(self) -> str:
        """Update downloads"""
        return os.path.join(self.local_app_data, 'updates')
    
    @property
    def update_download_path(self) -> str:
        """Downloaded update file"""
        return os.path.join(self.updates_dir, 'MyApp_Setup.exe')
    
    @property
    def rollback_dir(self) -> str:
        """Previous version backup for rollback"""
        return os.path.join(self.local_app_data, 'rollback')
    
    @property
    def previous_exe_path(self) -> str:
        """Previous version executable"""
        return os.path.join(self.rollback_dir, 'QuanLyB2B.exe')
    
    def get_temp_path(self, filename: str) -> str:
        """Get temporary file path"""
        return os.path.join(self.updates_dir, f"temp_{filename}")
