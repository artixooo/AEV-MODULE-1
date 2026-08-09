from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


def save_refresh_token(
    db: Session,
    email: str,
    token: str
):

    refresh_token = RefreshToken(
        email=email,
        token=token
    )

    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)

    return refresh_token


def get_refresh_token(
    db: Session,
    token: str
):

    return db.query(
        RefreshToken
    ).filter(
        RefreshToken.token == token
    ).first()