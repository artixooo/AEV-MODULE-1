from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.services.auth_service import (
    TokenInvalidError,
    decode_access_token,
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)


async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
) -> str:
    payload = decode_access_token(token)

    user_id = payload.get("sub")

    if user_id is None:
        raise TokenInvalidError(
            detail="Token payload is missing the subject (sub) claim",
            error_code="INVALID_TOKEN_PAYLOAD",
        )

    return str(user_id)
