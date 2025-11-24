from __future__ import annotations
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv('PROJECT_NAME','Rate Cards API')
    PROJECT_VERSION: str = os.getenv('PROJECT_VERSION','1.0.0')
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS','*')
    DATABASE_URL: str = os.getenv('DATABASE_URL','sqlite:///./test.db')
    GCS_BUCKET: str = os.getenv('GCS_BUCKET','')
    GCS_UPLOAD_PREFIX: str = os.getenv('GCS_UPLOAD_PREFIX','rate-cards')
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv('GOOGLE_APPLICATION_CREDENTIALS','') 
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings()
