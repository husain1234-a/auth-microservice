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
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    class Config:
        env_file = ".env"

settings = Settings()