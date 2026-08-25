import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Secrets Service"
    PORT: int = int(os.getenv("PORT", 8003))
    VAULT_ADDR: str = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
    VAULT_TOKEN: str = os.getenv("VAULT_TOKEN", "")

    class Config:
        env_file = ".env"

settings = Settings()