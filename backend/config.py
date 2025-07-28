from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Runway API
    RUNWAY_API_KEY: str
    
    # Application
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # File Upload
    MAX_FILE_SIZE: int = 16777216  # 16MB in bytes
    UPLOAD_DIRECTORY: str = "./uploads"
    JOBS_DIRECTORY: str = "./jobs"
    
    class Config:
        env_file = ".env"

settings = Settings() 