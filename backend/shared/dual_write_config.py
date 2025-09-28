"""
Configuration management for dual-write functionality during database migration.
"""

import os
from typing import Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DualWriteSettings:
    """Settings for dual-write behavior during migration"""
    
    # Core dual-write settings
    enabled: bool = True
    write_to_legacy: bool = True
    write_to_new: bool = True
    
    # Error handling
    fail_on_legacy_error: bool = False
    fail_on_new_error: bool = True
    
    # Validation settings
    validate_sync: bool = True
    sync_validation_interval: int = 300  # 5 minutes
    
    # Performance settings
    async_legacy_writes: bool = True
    batch_size: int = 100
    
    # Monitoring settings
    log_all_operations: bool = False
    log_errors_only: bool = True
    metrics_enabled: bool = True
    
    @classmethod
    def from_env(cls, service_name: str = "") -> 'DualWriteSettings':
        """Create settings from environment variables"""
        prefix = f"{service_name.upper()}_" if service_name else ""
        
        return cls(
            enabled=cls._get_bool_env(f"{prefix}DUAL_WRITE_ENABLED", True),
            write_to_legacy=cls._get_bool_env(f"{prefix}DUAL_WRITE_TO_LEGACY", True),
            write_to_new=cls._get_bool_env(f"{prefix}DUAL_WRITE_TO_NEW", True),
            fail_on_legacy_error=cls._get_bool_env(f"{prefix}DUAL_WRITE_FAIL_ON_LEGACY_ERROR", False),
            fail_on_new_error=cls._get_bool_env(f"{prefix}DUAL_WRITE_FAIL_ON_NEW_ERROR", True),
            validate_sync=cls._get_bool_env(f"{prefix}DUAL_WRITE_VALIDATE_SYNC", True),
            sync_validation_interval=cls._get_int_env(f"{prefix}DUAL_WRITE_SYNC_INTERVAL", 300),
            async_legacy_writes=cls._get_bool_env(f"{prefix}DUAL_WRITE_ASYNC_LEGACY", True),
            batch_size=cls._get_int_env(f"{prefix}DUAL_WRITE_BATCH_SIZE", 100),
            log_all_operations=cls._get_bool_env(f"{prefix}DUAL_WRITE_LOG_ALL", False),
            log_errors_only=cls._get_bool_env(f"{prefix}DUAL_WRITE_LOG_ERRORS_ONLY", True),
            metrics_enabled=cls._get_bool_env(f"{prefix}DUAL_WRITE_METRICS_ENABLED", True)
        )
    
    @staticmethod
    def _get_bool_env(key: str, default: bool) -> bool:
        """Get boolean environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    @staticmethod
    def _get_int_env(key: str, default: int) -> int:
        """Get integer environment variable"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            logger.warning(f"Invalid integer value for {key}, using default: {default}")
            return default
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            'enabled': self.enabled,
            'write_to_legacy': self.write_to_legacy,
            'write_to_new': self.write_to_new,
            'fail_on_legacy_error': self.fail_on_legacy_error,
            'fail_on_new_error': self.fail_on_new_error,
            'validate_sync': self.validate_sync,
            'sync_validation_interval': self.sync_validation_interval,
            'async_legacy_writes': self.async_legacy_writes,
            'batch_size': self.batch_size,
            'log_all_operations': self.log_all_operations,
            'log_errors_only': self.log_errors_only,
            'metrics_enabled': self.metrics_enabled
        }


class DualWriteConfigManager:
    """Manages dual-write configuration across services"""
    
    def __init__(self):
        self._settings_cache: Dict[str, DualWriteSettings] = {}
    
    def get_settings(self, service_name: str) -> DualWriteSettings:
        """Get dual-write settings for a service"""
        if service_name not in self._settings_cache:
            self._settings_cache[service_name] = DualWriteSettings.from_env(service_name)
            logger.info(f"Loaded dual-write settings for {service_name}: {self._settings_cache[service_name].to_dict()}")
        
        return self._settings_cache[service_name]
    
    def update_settings(self, service_name: str, **kwargs) -> None:
        """Update settings for a service"""
        current_settings = self.get_settings(service_name)
        
        # Update only provided fields
        for key, value in kwargs.items():
            if hasattr(current_settings, key):
                setattr(current_settings, key, value)
                logger.info(f"Updated {service_name} dual-write setting {key} = {value}")
            else:
                logger.warning(f"Unknown dual-write setting: {key}")
    
    def disable_dual_write(self, service_name: str) -> None:
        """Disable dual-write for a service"""
        self.update_settings(service_name, enabled=False)
        logger.info(f"Dual-write disabled for {service_name}")
    
    def enable_dual_write(self, service_name: str) -> None:
        """Enable dual-write for a service"""
        self.update_settings(service_name, enabled=True)
        logger.info(f"Dual-write enabled for {service_name}")
    
    def switch_to_new_db_only(self, service_name: str) -> None:
        """Switch service to write only to new database"""
        self.update_settings(
            service_name,
            write_to_legacy=False,
            write_to_new=True,
            fail_on_legacy_error=False
        )
        logger.info(f"Switched {service_name} to new database only")
    
    def switch_to_legacy_db_only(self, service_name: str) -> None:
        """Switch service to write only to legacy database"""
        self.update_settings(
            service_name,
            write_to_legacy=True,
            write_to_new=False,
            fail_on_new_error=False
        )
        logger.info(f"Switched {service_name} to legacy database only")
    
    def get_all_settings(self) -> Dict[str, Dict[str, Any]]:
        """Get all service settings"""
        return {
            service: settings.to_dict()
            for service, settings in self._settings_cache.items()
        }


# Global configuration manager instance
config_manager = DualWriteConfigManager()