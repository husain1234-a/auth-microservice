from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://poc_user:admin123@localhost:5432/poc"
    
    # JWT
    jwt_secret_key: str = "your_secret_key_here"
    jwt_algorithm: str = "HS256"
    
    # App
    app_name: str = "Order Service"
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # External Services
    user_service_url: str = "http://localhost:8001"
    product_service_url: str = "http://localhost:8002"
    cart_service_url: str = "http://localhost:8003"
    payment_service_url: str = "http://localhost:8005"  # Placeholder for payment service
    notification_service_url: str = "http://localhost:8006"  # Placeholder for notification service
    
    # Redis for async tasks
    redis_url: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"

settings = Settings()