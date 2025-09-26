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
    product_service_url: str = "http://localhost:8002"
    user_service_url: str = "http://localhost:8001"
    
    # Firebase Configuration
    firebase_project_id: str
    firebase_private_key_id: str
    firebase_private_key: str
    firebase_client_email: str
    firebase_client_id: str
    firebase_auth_uri: str
    firebase_token_uri: str
    firebase_client_cert_url: str
    
    # Session Configuration
    session_cookie_name: str = "auth_session"
    
    class Config:
        env_file = ".env"

settings = Settings()