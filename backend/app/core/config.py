from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List
import json

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    nixtla_api_key: str
    app_env: str = "development"
    log_level: str = "INFO"
    cache_ttl_seconds: int = 3600
    cache_dir: str = ".cache"
    cors_origins: List[str] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            return json.loads(v)
        raise ValueError("Invalid CORS_ORIGINS format")

    @property
    def is_production(self) -> bool:
       return self.app_env.lower() == "production"
        
settings = Settings() 

#what this file does
#Loads settings from .env + gives them to your app