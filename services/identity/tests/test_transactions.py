from datetime import datetime, timedelta, timezone
import uuid

from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.session import Session as SessionModel
from app.models.refresh_token import RefreshToken
from app.repositories.session_repository import create_session
from app.repositories.refresh_token_repository import create_refresh_token

TENANT_ID = uuid.UUID(
    "11111111-1111-1111-1111-111111111111"
)


def test_transaction_rollback(db_session):
    user = User(
        tenant_id=TENANT_ID,
        username=f"rollback_{uuid.uuid4().hex[:8]}",
        email=f"rollback_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="test-hash",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    refresh_token = "rollback-refresh-token"

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(days=7)
    )

    session = create_session(
        db=db_session,
        user_id=user.id,
        tenant_id=user.tenant_id,
        expires_at=expires_at,
    )

    create_refresh_token(
        db=db_session,
        user_id=user.id,
        session_id=session.id,
        token=refresh_token,
        expires_at=expires_at,
    )

    # Force a failure by inserting the same refresh token again.
    try:
        create_refresh_token(
            db=db_session,
            user_id=user.id,
            session_id=session.id,
            token=refresh_token,
            expires_at=expires_at,
        )

        db_session.commit()

        assert False, "Expected IntegrityError"

    except IntegrityError:
        db_session.rollback()

    # Because the session and refresh token were never committed,
    # the transaction rollback removes them.
    assert (
        db_session.query(SessionModel)
        .filter(SessionModel.id == session.id)
        .first()
        is None
    )
    assert (
        db_session.query(RefreshToken)
        .filter(RefreshToken.session_id == session.id)
        .first()
        is None
    )