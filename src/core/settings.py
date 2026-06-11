# -*- coding: utf-8 -*-
"""
Settings and configuration management
"""
import json
import os
from typing import Any, Dict, Optional


class Settings:
    """Application settings manager"""
    
    DEFAULT_SETTINGS = {
        'app': {
            'theme': 'light',  # 'light' or 'dark'
            'language': 'vi',
            'check_updates_on_startup': True,
            'last_update_check': None,
            'skipped_version': None,
        },
        'update': {
            'auto_download': False,
            'download_path': None,
        },
        'window': {
            'width': 1600,
            'height': 1000,
            'maximized': False,
        },
        'excel': {
            'default_export_format': 'xlsx',
            'max_rows_per_sheet': 100000,
        },
    }
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self._settings = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load settings from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_settings = json.load(f)
                
                # Merge with defaults
                return self._merge_dicts(self.DEFAULT_SETTINGS, user_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.DEFAULT_SETTINGS.copy()
        
        return self.DEFAULT_SETTINGS.copy()
    
    def _merge_dicts(self, defaults: dict, user: dict) -> dict:
        """Deep merge dictionaries"""
        result = defaults.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        return result
    
    def save(self):
        """Save settings to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value"""
        keys = key.split('.')
        value = self._settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set setting value"""
        keys = key.split('.')
        target = self._settings
        
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        target[keys[-1]] = value
    
    def reset(self, key: str = None):
        """Reset settings to defaults"""
        if key:
            keys = key.split('.')
            target = self._settings
            default = self.DEFAULT_SETTINGS
            
            for k in keys[:-1]:
                target = target.get(k, {})
                default = default.get(k, {})
            
            target[keys[-1]] = default.get(keys[-1])
        else:
            self._settings = self.DEFAULT_SETTINGS.copy()
        
        self.save()
    
    @property
    def theme(self) -> str:
        """Get current theme"""
        return self.get('app.theme', 'light')
    
    @theme.setter
    def theme(self, value: str):
        """Set theme"""
        self.set('app.theme', value)
        self.save()
    
    @property
    def skipped_version(self) -> Optional[str]:
        """Get skipped version"""
        return self.get('app.skipped_version')
    
    @skipped_version.setter
    def skipped_version(self, version: str):
        """Set skipped version"""
        self.set('app.skipped_version', version)
        self.save()
    
    @property
    def last_update_check(self) -> Optional[str]:
        """Get last update check timestamp"""
        return self.get('app.last_update_check')
    
    @last_update_check.setter
    def last_update_check(self, timestamp: str):
        """Set last update check timestamp"""
        self.set('app.last_update_check', timestamp)
        self.save()
