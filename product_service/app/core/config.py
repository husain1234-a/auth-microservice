from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/product_db"
    
    # JWT
    jwt_secret_key: str = "your_secret_key_here"
    jwt_algorithm: str = "HS256"
    
    # App
    app_name: str = "Product Service"
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Cloudflare R2
    r2_endpoint_url: str = "https://your-account.r2.cloudflarestorage.com"
    r2_access_key_id: str = "your_access_key_id"
    r2_secret_access_key: str = "your_secret_access_key"
    r2_bucket_name: str = "product-images"
    r2_region: str = "auto"
    
    class Config:
        env_file = ".env"


settings = Settings()