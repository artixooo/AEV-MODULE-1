"""
Authentication Middleware — JWT validation for Policy Service.

Validates the same JWT tokens issued by the Identity Service, using the
shared JWT_SECRET_KEY/JWT_ALGORITHM (symmetric signing — the same secret
both creates and verifies the token, so this service does not need to
call out to Identity Service for every request).

Scope note: the token currently issued by Identity Service carries only
a `sub` (the user's email) and `exp` claim — no role information. This
middleware therefore only proves *who* is calling (authentication); it
does not determine *what role* they have. Callers must supply the role
to check explicitly (e.g. as a request parameter to /evaluate), since no
service in this system currently maps a user to a role.

Author: Utkarsh Pratham (Squad Lead) & Narayanan Varadarajan
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

from dataclasses import dataclass

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.core.config import settings

security = HTTPBearer()


@dataclass
class AuthenticatedUser:
    """The identity extracted from a validated JWT."""
    email: str
    raw_claims: dict


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthenticatedUser:
    """
    FastAPI dependency: validates the Bearer token on the request.

    Raises:
        HTTPException(401) if the token is missing, malformed, expired,
        or signed with a different secret than this service expects.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token missing subject claim")

    return AuthenticatedUser(email=email, raw_claims=payload)