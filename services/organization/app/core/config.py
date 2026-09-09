from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Organization Service"
    APP_ENV: str = "development"
    PORT: int = 8001

    DATABASE_URL: str

    # Authentication configuration
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"

    # Identity Service integration
    IDENTITY_SERVICE_URL: str = "http://identity:8000"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()