from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from typing import List, Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    CORS_ORIGINS: List[str] = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    app_name: str = "Banalyze Backend"
    log_level: str = "INFO"
    port: int = 8000
    reload: bool = True
    env: str = "development"
    debug_mode: bool = True
    base_url: str = Field(alias="BASE_URL", default="http://localhost:8000")
 
    # DB Configuration
    db_host: str = "localhost"
    db_port: str = "5432"
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_database: str = "banalyze_db"
    db_echo: bool = True
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_database}"
    
    # JWT Authentication Configuration
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY", default="super_secret_default_key")
    jwt_refresh_secret_key: str = Field(alias="JWT_REFRESH_SECRET_KEY", default="super_secret_refresh_default_key")
    jwt_algorithm: str = Field(alias="JWT_ALGORITHM", default="HS256")
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Redis Configuration
    redis_url: str = ""
    

settings = Settings()
