from datetime import timedelta

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.utils.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
)


def credentials(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )


def test_access_token_is_valid():
    token = create_access_token(
        {
            "sub": "user-123",
            "email": "user@example.com",
            "tenant_id": "tenant-123",
        }
    )

    payload = verify_token(credentials(token))

    assert payload["sub"] == "user-123"
    assert payload["email"] == "user@example.com"
    assert payload["tenant_id"] == "tenant-123"
    assert payload["type"] == "access"


def test_refresh_token_is_not_accepted_as_access_token():
    token = create_refresh_token(
        {
            "sub": "user-123",
            "email": "user@example.com",
            "tenant_id": "tenant-123",
        }
    )

    with pytest.raises(HTTPException) as exc:
        verify_token(credentials(token))

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid access token"


def test_refresh_token_decodes_with_refresh_type():
    token = create_refresh_token(
        {
            "sub": "user-123",
            "email": "user@example.com",
            "tenant_id": "tenant-123",
        }
    )

    payload = decode_token(token)

    assert payload is not None
    assert payload["sub"] == "user-123"
    assert payload["type"] == "refresh"


def test_invalid_token_is_rejected():
    with pytest.raises(HTTPException) as exc:
        verify_token(credentials("invalid.jwt.token"))

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid or expired token"


def test_expired_access_token_is_rejected():
    token = create_access_token(
        {"sub": "user-123"},
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(HTTPException) as exc:
        verify_token(credentials(token))

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid or expired token"
