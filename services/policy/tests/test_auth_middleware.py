"""
Auth Middleware Security Tests — verifies JWT algorithm restriction and
rejection of expired/malformed tokens, per issue #61 review point 3.

Author: Pod Alpha Security Engineering
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from app.core.config import settings
from app.middleware.auth_middleware import get_current_user

_app = FastAPI()


@_app.get("/protected")
def _protected(user=Depends(get_current_user)):
    return {"email": user.email}


client = TestClient(_app)


def _valid_payload():
    return {"sub": "alice@example.com", "exp": datetime.now(timezone.utc) + timedelta(minutes=30)}


def test_correctly_signed_token_is_accepted():
    token = jwt.encode(_valid_payload(), settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "alice@example.com"


def test_wrong_algorithm_is_rejected_even_with_correct_secret():
    """
    Proves the algorithm itself is checked, not just the secret — a token
    signed with the same secret but a different algorithm (HS384 instead
    of the configured HS256) must still be rejected.
    """
    token = jwt.encode(_valid_payload(), settings.JWT_SECRET_KEY, algorithm="HS384")
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_another_wrong_algorithm_is_rejected():
    token = jwt.encode(_valid_payload(), settings.JWT_SECRET_KEY, algorithm="HS512")
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_expired_token_is_rejected():
    payload = {"sub": "alice@example.com", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_malformed_token_is_rejected():
    response = client.get("/protected", headers={"Authorization": "Bearer this.is.not.a.jwt"})
    assert response.status_code == 401