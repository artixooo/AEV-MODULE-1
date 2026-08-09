from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str
    APP_ENV: str

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    DATABASE_URL: str

    REDIS_HOST: str
    REDIS_PORT: int

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str


    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()