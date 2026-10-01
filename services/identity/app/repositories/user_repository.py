from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email(
    db: Session,
    email: str,
):
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def get_user_by_username(
    db: Session,
    username: str,
):
    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def get_user_by_email_or_username(
    db: Session,
    identifier: str,
):
    return (
        db.query(User)
        .filter(
            (User.email == identifier)
            | (User.username == identifier)
        )
        .first()
    )