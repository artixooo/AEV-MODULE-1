"""
Policy Service Configuration Module.

This module defines the application configuration settings using Pydantic Settings.
Environment variables are automatically validated and loaded with default fallback values.

Author: Pod Alpha Security Engineering
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

import os
from pydantic import model_validator
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
        JWT_SECRET_KEY (str): Shared secret for validating JWTs issued by the Identity Service.
        JWT_ALGORITHM (str): Signing algorithm used for JWT validation (must match Identity Service).
        POLICY_CACHE_TTL (int): Time-to-Live (in seconds) for permission decision caching.
        ENABLE_SOD_ENFORCEMENT (bool): Flag to enforce Segregation of Duties policy rules.
    """
    APP_NAME: str = "policy-service"
    APP_ENV: str = "development"
    PORT: int = 8002
    HOST: str = "0.0.0.0"

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/pod_alpha"
    REDIS_URL: str = "redis://localhost:6379"

        # NOTE: reserved for future use — Identity Service does not yet expose
    # a role-lookup, so nothing in this codebase actually calls this URL yet.
    IDENTITY_SERVICE_URL: str = "http://localhost:8000"
    ORGANIZATION_SERVICE_URL: str = "http://localhost:8001"

    # Shared JWT signing secret — must match the value identity uses
    # (services/identity/app/core/config.py), since tokens are validated
    # with the same key that created them, not fetched from identity.
    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"

    # Shared secret for trusted internal service-to-service calls
    # (e.g. from the API Gateway). Required on POST /evaluate — see
    # app/middleware/service_auth_middleware.py for why.
    SERVICE_API_KEY: str = "change-me"

    POLICY_CACHE_TTL: int = 300
    ENABLE_SOD_ENFORCEMENT: bool = True

    # Comma-separated list of allowed frontend/gateway origins for CORS.
    # Defaults to localhost for local dev; set explicitly per environment.
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

    @model_validator(mode="after")
    def _forbid_default_secrets_outside_dev(self) -> "Settings":
        """
        Refuse to start with placeholder secrets anywhere other than local
        development. Prevents a misconfigured staging/production deployment
        from silently running with JWT_SECRET_KEY / SERVICE_API_KEY still
        set to the insecure "change-me" default.
        """
        if self.APP_ENV != "development":
            insecure = [
                name for name, value in (
                    ("JWT_SECRET_KEY", self.JWT_SECRET_KEY),
                    ("SERVICE_API_KEY", self.SERVICE_API_KEY),
                )
                if value == "change-me"
            ]
            if insecure:
                raise ValueError(
                    f"Refusing to start with default placeholder value(s) for "
                    f"{', '.join(insecure)} outside development (APP_ENV={self.APP_ENV!r}). "
                    f"Set these via real environment variables or a secrets manager."
                )
        return self


# Global Singleton Settings Instance
settings = Settings()
