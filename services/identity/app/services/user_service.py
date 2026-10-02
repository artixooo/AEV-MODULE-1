import uuid

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user_schema import UserCreate
from app.services.auth_service import hash_password


def get_user_by_id(
    db: Session,
    user_id: uuid.UUID
):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def create_user(
    db: Session,
    user: UserCreate,
    tenant_id: uuid.UUID
):
    password_hash = hash_password(
        user.password
    )

    new_user = User(
        tenant_id=tenant_id,
        username=user.username,
        email=user.email,
        password_hash=password_hash
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user