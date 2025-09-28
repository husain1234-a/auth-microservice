from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://poc_user:admin123@localhost:5432/product_db"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "product_db"
    database_user: str = "poc_user"
    database_password: str = "admin123"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    
    # Legacy Database (for dual-write during migration)
    legacy_database_url: Optional[str] = None
    
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
    
    # JWT
    jwt_secret_key: str = "your_secret_key_here"
    jwt_algorithm: str = "HS256"
    
    # App
    app_name: str = "Product Service"
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Cloudflare R2
    r2_endpoint_url: str = "https://27092aebbf9f81d4598314d98e346ef5.r2.cloudflarestorage.com"
    r2_access_key_id: str = "236addec90677dca275aa7d5deade31e"
    r2_secret_access_key: str = "0b866d97ea246c4442c2445fbbd54e34adc243d9a608272ec62d6f023173f302"
    r2_bucket_name: str = "grofast-assets"
    r2_region: str = "auto"
    # Public URL for direct access (set up custom domain or use R2.dev subdomain)
    r2_public_url: str = "https://pub-2f9001567501480bac2457f2d7a410ba.r2.dev"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from .env


settings = Settings()