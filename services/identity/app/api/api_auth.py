"""
Request and response models for the Authentication API (v1).
"""
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """Credentials submitted to POST /api/v1/auth/login."""
    email: EmailStr = Field(..., description="User's registered email address")
    password: str = Field(..., min_length=8, max_length=128, description="Plaintext password")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "user@example.com",
            "password": "SuperSecret123!",
        }
    })


class RefreshRequest(BaseModel):
    """Body for POST /api/v1/auth/refresh."""
    refresh_token: str = Field(..., description="Valid refresh token issued at login")


class LogoutRequest(BaseModel):
    """Body for POST /api/v1/auth/logout."""
    refresh_token: str = Field(..., description="Refresh token to revoke")


class TokenResponse(BaseModel):
    """Returned by POST /api/v1/auth/login."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token TTL in seconds")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 900,
        }
    })


class RefreshResponse(BaseModel):
    """
    Returned by POST /api/v1/auth/refresh.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token TTL in seconds")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 900,
        }
    })


class LogoutResponse(BaseModel):
    """Returned by POST /api/v1/auth/logout."""
    message: str = "Successfully logged out"


class AuthErrorResponse(BaseModel):
    """
    Flat error shape returned on every 401 across login/refresh/logout:
        {"detail": "...", "error_code": "..."}
    """
    detail: str
    error_code: str

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "detail": "Invalid email or password",
            "error_code": "INVALID_CREDENTIALS",
        }
    })
