from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.user_schema import (
    UserCreate,
    UserLogin,
    UserResponse
)

from app.services.user_service import (
    create_user,
    get_user_by_email
)

from app.services.auth_service import (
    verify_password,
    create_access_token
)

from app.utils.jwt import (
    create_refresh_token,
    verify_token,
    decode_token
)

from app.services.token_service import (
    save_refresh_token,
    get_refresh_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ==========================
# Register User
# ==========================

@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = get_user_by_email(
        db,
        user.email
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    return create_user(
        db,
        user
    )


# ==========================
# Login User
# ==========================

@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    db_user = get_user_by_email(
        db,
        user.email
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )


    if not verify_password(
        user.password,
        db_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )


    access_token = create_access_token(
        {
            "sub": db_user.email
        }
    )


    refresh_token = create_refresh_token(
        {
            "sub": db_user.email
        }
    )


    save_refresh_token(
        db,
        db_user.email,
        refresh_token
    )


    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }



# ==========================
# Protected Profile API
# ==========================

@router.get("/profile")
def profile(
    payload: dict = Depends(verify_token)
):

    return {
        "message": "JWT verification successful",
        "user": payload.get("sub")
    }



# ==========================
# Refresh Access Token
# ==========================

@router.post("/refresh")
def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):

    stored_token = get_refresh_token(
        db,
        refresh_token
    )


    if not stored_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )


    payload = decode_token(
        refresh_token
    )


    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Expired refresh token"
        )


    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type"
        )


    email = payload.get("sub")


    new_access_token = create_access_token(
        {
            "sub": email
        }
    )


    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }