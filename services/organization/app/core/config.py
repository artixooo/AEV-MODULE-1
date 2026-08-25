from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Organization Service"
    APP_ENV: str = "development"
    PORT: int = 8001

    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/pod_alpha"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()