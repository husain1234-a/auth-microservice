from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database - Cart Service Isolated Database
    database_url: str = "postgresql+asyncpg://poc_user:admin123@localhost:5432/cart_db"
    database_host: str = "localhost"
    database_port: str = "5432"
    database_name: str = "cart_db"
    database_user: str = "poc_user"
    database_password: str = "admin123"
    database_pool_size: str = "10"
    database_max_overflow: str = "20"
    database_pool_timeout: str = "30"
    database_pool_recycle: str = "3600"
    
    # Legacy Database (for dual-write during migration)
    legacy_database_url: str = "postgresql+asyncpg://poc_user:admin123@localhost:5432/poc"
    
    # Dual-Write Configuration
    dual_write_enabled: str = "true"
    dual_write_to_legacy: str = "true"
    dual_write_to_new: str = "true"
    dual_write_fail_on_legacy_error: str = "false"
    dual_write_fail_on_new_error: str = "true"
    dual_write_validate_sync: str = "true"
    dual_write_sync_interval: str = "300"
    dual_write_async_legacy: str = "true"
    dual_write_batch_size: str = "100"
    dual_write_log_all: str = "false"
    dual_write_log_errors_only: str = "true"
    dual_write_metrics_enabled: str = "true"
    
    # JWT
    jwt_secret_key: str = "your_secret_key_here"
    jwt_algorithm: str = "HS256"
    
    # App
    app_name: str = "Cart Service"
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # External Services
    product_service_url: str = "http://localhost:8002"
    user_service_url: str = "http://localhost:8001"
    
    # Firebase Configuration
    firebase_project_id: str = ""
    firebase_private_key_id: str = ""
    firebase_private_key: str = ""
    firebase_client_email: str = ""
    firebase_client_id: str = ""
    firebase_auth_uri: str = ""
    firebase_token_uri: str = ""
    firebase_client_cert_url: str = ""
    
    # Session Configuration
    session_cookie_name: str = "auth_session"
    
    class Config:
        env_file = ".env"

settings = Settings()