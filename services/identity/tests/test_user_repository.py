from app.models.user import User

from app.repositories.user_repository import (
    get_user_by_email,
    get_user_by_username,
    get_user_by_email_or_username,
)


def test_user_lookup_by_email(db_session):
    user = User(
        tenant_id="11111111-1111-1111-1111-111111111111",
        username="pytest_email_user",
        email="pytest_email@example.com",
        password_hash="test-hash",
    )

    db_session.add(user)
    db_session.commit()

    result = get_user_by_email(
        db_session,
        "pytest_email@example.com",
    )

    assert result is not None
    assert result.email == "pytest_email@example.com"


def test_user_lookup_by_username(db_session):
    user = User(
        tenant_id="11111111-1111-1111-1111-111111111111",
        username="pytest_username_user",
        email="pytest_username@example.com",
        password_hash="test-hash",
    )

    db_session.add(user)
    db_session.commit()

    result = get_user_by_username(
        db_session,
        "pytest_username_user",
    )

    assert result is not None
    assert result.username == "pytest_username_user"


def test_user_lookup_by_email_or_username(db_session):
    user = User(
        tenant_id="11111111-1111-1111-1111-111111111111",
        username="pytest_both_user",
        email="pytest_both@example.com",
        password_hash="test-hash",
    )

    db_session.add(user)
    db_session.commit()

    result_by_email = get_user_by_email_or_username(
        db_session,
        "pytest_both@example.com",
    )

    result_by_username = get_user_by_email_or_username(
        db_session,
        "pytest_both_user",
    )

    assert result_by_email is not None
    assert result_by_username is not None