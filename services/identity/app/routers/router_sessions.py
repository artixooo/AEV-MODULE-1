"""
Session management API.

Endpoints:
- GET  /api/v1/auth/sessions
- GET  /api/v1/auth/sessions/{session_id}
- POST /api/v1/auth/sessions/{session_id}/revoke
- POST /api/v1/auth/sessions/revoke-all
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.api_auth import (
    SessionActionResponse,
    SessionListResponse,
    SessionResponse,
)
from app.api.api_auth_deps import get_current_user_id
from app.core.database import get_db
from app.models.session import Session as SessionModel
from app.repositories.refresh_token_repository import (
    revoke_refresh_tokens_by_session,
    revoke_refresh_tokens_by_sessions,
)
from app.repositories.session_repository import (
    cleanup_expired_sessions,
    get_session_by_id,
    get_sessions_by_user,
    revoke_session,
    revoke_sessions_by_user,
)
from app.models.user import User


router = APIRouter(
    prefix="/api/v1/auth/sessions",
    tags=["Sessions"],
)


def _session_response(
    session: SessionModel,
) -> SessionResponse:
    return SessionResponse(
        id=str(session.id),
        user_id=str(session.user_id),
        tenant_id=str(session.tenant_id),
        device_name=session.device_name,
        device_type=session.device_type,
        ip_address=session.ip_address,
        user_agent=session.user_agent,
        is_active=session.is_active,
        expires_at=session.expires_at.isoformat(),
        last_activity=(
            session.last_activity.isoformat()
            if session.last_activity
            else None
        ),
        created_at=(
            session.created_at.isoformat()
            if session.created_at
            else None
        ),
    )


def _get_authenticated_user(
    db: Session,
    user_id: str,
) -> User:
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user not found",
        )

    return user


def _get_owned_session(
    db: Session,
    session_id: str,
    user_id: str,
) -> SessionModel:
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid session identifier",
        )

    session = get_session_by_id(
        db=db,
        session_id=session_uuid,
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    if str(session.user_id) != str(user_id):
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    user = _get_authenticated_user(
        db=db,
        user_id=user_id,
    )

    if str(session.tenant_id) != str(user.tenant_id):
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return session


@router.get(
    "",
    response_model=SessionListResponse,
    summary="List authenticated user's sessions",
)
def list_sessions(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> SessionListResponse:
    cleanup_expired_sessions(db)

    sessions = get_sessions_by_user(
        db=db,
        user_id=user_id,
    )

    db.commit()

    return SessionListResponse(
        sessions=[
            _session_response(session)
            for session in sessions
        ]
    )


@router.post(
    "/revoke-all",
    response_model=SessionActionResponse,
    summary="Revoke all sessions owned by the authenticated user",
)
def revoke_all_sessions(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> SessionActionResponse:
    sessions = revoke_sessions_by_user(
        db=db,
        user_id=user_id,
    )

    session_ids = [
        session.id
        for session in sessions
    ]

    revoke_refresh_tokens_by_sessions(
        db=db,
        session_ids=session_ids,
    )

    db.commit()

    return SessionActionResponse(
        message="All sessions revoked successfully",
    )

@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Get a session owned by the authenticated user",
)
def get_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> SessionResponse:
    session = _get_owned_session(
        db=db,
        session_id=session_id,
        user_id=user_id,
    )

    return _session_response(session)


@router.post(
    "/{session_id}/revoke",
    response_model=SessionActionResponse,
    summary="Revoke an authenticated user's session",
)
def revoke_user_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> SessionActionResponse:
    session = _get_owned_session(
        db=db,
        session_id=session_id,
        user_id=user_id,
    )

    session = revoke_session(
        db=db,
        session=session,
    )

    revoke_refresh_tokens_by_session(
        db=db,
        session_id=session.id,
    )

    db.commit()

    return SessionActionResponse(
        message="Session revoked successfully",
        session_id=str(session.id),
    )
