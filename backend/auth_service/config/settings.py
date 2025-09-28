import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    firebase_project_id: str
    firebase_private_key_id: str
    firebase_private_key: str
    firebase_client_email: str
    firebase_client_id: str
    firebase_auth_uri: str
    firebase_token_uri: str
    firebase_client_cert_url: str
    
    redis_url: str = "redis://localhost:6379"
    cors_origins: str = "http://localhost:3000"
    session_cookie_name: str = "auth_session"
    environment: str = "development"
    database_url: str
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "auth_db"
    database_user: str = "poc_user"
    database_password: str = "admin123"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    
    # Legacy Database (for dual-write during migration)
    legacy_database_url: str = None
    
    # Dual-Write Configuration
    dual_write_enabled: bool = True
    dual_write_to_legacy: bool = True
    dual_write_to_new: bool = True
    dual_write_fail_on_legacy_error: bool = False
    dual_write_fail_on_new_error: bool = True
    dual_write_validate_sync: bool = True
    dual_write_sync_interval: int = 300
    dual_write_async_legacy: bool = True
    dual_write_batch_size: int = 100
    dual_write_log_all: bool = False
    dual_write_log_errors_only: bool = True
    dual_write_metrics_enabled: bool = True 
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from .env

settings = Settings()