from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://poc_user:admin123@localhost:5432/poc"
    
    # JWT
    jwt_secret_key: str = "your_secret_key_here"
    jwt_algorithm: str = "HS256"
    
    # App
    app_name: str = "Cart Service"
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # External Services
    product_service_url: str = "http://product-service:8002"
    user_service_url: str = "http://user-service:8001"
    
    class Config:
        env_file = ".env"

settings = Settings()