import pytest
import jwt
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import (
    get_bearer_token,
    validate_jwt_claims,
)


def test_bearer_token_extraction():
    class MockRequest:
        headers = {
            "Authorization": "Bearer test-token"
        }

    token = get_bearer_token(MockRequest())

    assert token == "test-token"


def test_missing_authorization_header():
    class MockRequest:
        headers = {}

    with pytest.raises(HTTPException) as exc:
        get_bearer_token(MockRequest())

    assert exc.value.status_code == 401


def test_invalid_authorization_scheme():
    class MockRequest:
        headers = {
            "Authorization": "Basic test-token"
        }

    with pytest.raises(HTTPException) as exc:
        get_bearer_token(MockRequest())

    assert exc.value.status_code == 401


def test_valid_jwt_claims():
    token = jwt.encode(
        {
            "sub": "user-123",
            "tenant_id": "tenant-456",
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    claims = validate_jwt_claims(token)

    assert claims["sub"] == "user-123"
    assert claims["tenant_id"] == "tenant-456"


def test_invalid_jwt_is_rejected():
    with pytest.raises(HTTPException) as exc:
        validate_jwt_claims("invalid-token")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid authentication token"


def test_jwt_missing_sub_is_rejected():
    token = jwt.encode(
        {
            "tenant_id": "tenant-456",
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc:
        validate_jwt_claims(token)

    assert exc.value.status_code == 401
    assert exc.value.detail == "JWT is missing required 'sub' claim"