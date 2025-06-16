"""
Configuration Manager
====================

Simplified configuration management để giảm complexity.
"""

import os
from typing import Dict, Any, Optional
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self):
        self._config_cache = {}
        self._default_values = {
            # App settings
            'app_name': 'Lab Manager',
            'app_description': 'Hệ thống quản lý phòng thực hành',
            'app_version': '1.0.0',
            
            # Security settings
            'enable_registration': True,
            'enable_password_reset': True,
            'csrf_enabled': True,
            'session_timeout': 3600,
            
            # Pagination settings
            'items_per_page': 20,
            'max_items_per_page': 100,
            
            # Cache settings
            'cache_timeout': 300,
            'api_cache_timeout': 120,
            
            # Email settings
            'mail_enabled': False,
            'mail_debug': False,
            
            # File upload settings
            'max_file_size': 16 * 1024 * 1024,  # 16MB
            'allowed_extensions': ['txt', 'pdf', 'doc', 'docx'],
            
            # Database settings
            'db_pool_size': 10,
            'db_pool_timeout': 30,
            
            # API settings
            'api_rate_limit': '100/hour',
            'api_version': 'v1'
        }
    
    def get(self, key: str, default: Any = None, use_cache: bool = True) -> Any:
        """Get configuration value"""
        # Check cache first
        if use_cache and key in self._config_cache:
            return self._config_cache[key]
        
        # Try environment variable first
        env_key = key.upper().replace('.', '_')
        value = os.getenv(env_key)
        
        if value is not None:
            # Convert string values to appropriate types
            value = self._convert_value(value)
        else:
            # Try database setting
            try:
                from ..models import CaiDatHeThong
                setting = CaiDatHeThong.lay_gia_tri(key)
                if setting is not None:
                    value = setting
                else:
                    # Use default value
                    value = self._default_values.get(key, default)
            except:
                # Fallback to default if database is not available
                value = self._default_values.get(key, default)
        
        # Cache the value
        if use_cache:
            self._config_cache[key] = value
        
        return value
    
    def set(self, key: str, value: Any, persist: bool = True, description: str = "") -> bool:
        """Set configuration value"""
        try:
            # Update cache
            self._config_cache[key] = value
            
            # Persist to database if requested
            if persist:
                from ..models import CaiDatHeThong, db
                
                # Determine value type
                value_type = self._get_value_type(value)
                
                CaiDatHeThong.dat_gia_tri(key, value, value_type, description or f"Setting for {key}")
                db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting config {key}: {str(e)}")
            return False
    
    def get_all(self, prefix: str = None) -> Dict[str, Any]:
        """Get all configuration values with optional prefix filter"""
        try:
            from ..models import CaiDatHeThong
            
            query = CaiDatHeThong.query
            if prefix:
                query = query.filter(CaiDatHeThong.khoa.like(f"{prefix}%"))
            
            settings = query.all()
            
            result = {}
            for setting in settings:
                result[setting.khoa] = setting.gia_tri
            
            # Add default values for missing keys
            for key, default_value in self._default_values.items():
                if prefix and not key.startswith(prefix):
                    continue
                if key not in result:
                    result[key] = default_value
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting all configs: {str(e)}")
            return self._default_values.copy()
    
    def update_multiple(self, settings: Dict[str, Any], persist: bool = True) -> bool:
        """Update multiple settings at once"""
        try:
            for key, value in settings.items():
                self.set(key, value, persist=False)  # Don't commit each one
            
            if persist:
                from ..models import db
                db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating multiple configs: {str(e)}")
            try:
                from ..models import db
                db.session.rollback()
            except:
                pass
            return False
    
    def reset_to_defaults(self, keys: list = None) -> bool:
        """Reset settings to default values"""
        try:
            keys_to_reset = keys or list(self._default_values.keys())
            
            for key in keys_to_reset:
                if key in self._default_values:
                    self.set(key, self._default_values[key], persist=False)
            
            from ..models import db
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error resetting configs: {str(e)}")
            return False
    
    def clear_cache(self, key: str = None) -> None:
        """Clear configuration cache"""
        if key:
            self._config_cache.pop(key, None)
        else:
            self._config_cache.clear()
    
    def validate_setting(self, key: str, value: Any) -> bool:
        """Validate setting value"""
        validators = {
            'items_per_page': lambda x: isinstance(x, int) and 1 <= x <= 100,
            'session_timeout': lambda x: isinstance(x, int) and x > 0,
            'max_file_size': lambda x: isinstance(x, int) and x > 0,
            'app_name': lambda x: isinstance(x, str) and len(x.strip()) > 0,
            'app_description': lambda x: isinstance(x, str),
            'enable_registration': lambda x: isinstance(x, bool),
            'enable_password_reset': lambda x: isinstance(x, bool),
        }
        
        validator = validators.get(key)
        if validator:
            return validator(value)
        
        return True  # Default to valid if no specific validator
    
    def _convert_value(self, value: str) -> Any:
        """Convert string value to appropriate type"""
        # Boolean values
        if value.lower() in ('true', '1', 'yes', 'on'):
            return True
        elif value.lower() in ('false', '0', 'no', 'off'):
            return False
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _get_value_type(self, value: Any) -> str:
        """Get value type for database storage"""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'float'
        else:
            return 'string'

# Global instance
config_manager = ConfigManager()

# Convenience functions
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return config_manager.get(key, default)

def set_config(key: str, value: Any, persist: bool = True, description: str = "") -> bool:
    """Set configuration value"""
    return config_manager.set(key, value, persist, description)

def get_all_config(prefix: str = None) -> Dict[str, Any]:
    """Get all configuration values"""
    return config_manager.get_all(prefix)

def update_config(settings: Dict[str, Any], persist: bool = True) -> bool:
    """Update multiple settings"""
    return config_manager.update_multiple(settings, persist)
