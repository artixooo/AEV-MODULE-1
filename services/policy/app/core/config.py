"""
Policy Service Configuration Module.

This module defines the application configuration settings using Pydantic Settings.
Environment variables are automatically validated and loaded with default fallback values.

Author: Utkarsh Pratham (Squad Leader) & Narayanan Varadarajan
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings Container.

    Attributes:
        APP_NAME (str): The unique identifier for the policy service.
        APP_ENV (str): Runtime environment ('development', 'staging', 'production').
        PORT (int): Service HTTP port listener (default: 8002).
        HOST (str): Network host binding interface.
        DATABASE_URL (str): Connection string for PostgreSQL database.
        REDIS_URL (str): Connection string for Redis cache cluster.
        IDENTITY_SERVICE_URL (str): Endpoint for upstream Identity Service.
        ORGANIZATION_SERVICE_URL (str): Endpoint for upstream Organization Service.
        POLICY_CACHE_TTL (int): Time-to-Live (in seconds) for permission decision caching.
        ENABLE_SOD_ENFORCEMENT (bool): Flag to enforce Segregation of Duties policy rules.
    """
    APP_NAME: str = "policy-service"
    APP_ENV: str = "development"
    PORT: int = 8002
    HOST: str = "0.0.0.0"

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/pod_alpha"
    REDIS_URL: str = "redis://localhost:6379"

    IDENTITY_SERVICE_URL: str = "http://localhost:8000"
    ORGANIZATION_SERVICE_URL: str = "http://localhost:8001"

    POLICY_CACHE_TTL: int = 300
    ENABLE_SOD_ENFORCEMENT: bool = True

    # Comma-separated list of allowed frontend/gateway origins for CORS.
    # Defaults to localhost for local dev; set explicitly per environment.
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]


# Global Singleton Settings Instance
settings = Settings()
