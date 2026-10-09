import uuid
from datetime import datetime, timedelta, timezone
from uuid import UUID
from app.models.session import Session as SessionModel

import pytest

from app.services.tenant_config_service import (
    DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    DEFAULT_MFA_ENABLED,
    DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS,
    DEFAULT_SESSION_EXPIRE_DAYS,
    TenantAuthConfig,
    DefaultTenantConfigurationProvider,
)


TENANT_A = UUID("11111111-1111-1111-1111-111111111111")
TENANT_B = UUID("22222222-2222-2222-2222-222222222222")


def test_tenant_config_uses_safe_defaults():
    config = TenantAuthConfig(tenant_id=TENANT_A)

    assert config.tenant_id == TENANT_A
    assert config.access_token_expire_minutes == DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES
    assert config.refresh_token_expire_days == DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS
    assert config.session_expire_days == DEFAULT_SESSION_EXPIRE_DAYS
    assert config.mfa_enabled is DEFAULT_MFA_ENABLED


def test_tenant_config_keeps_tenants_isolated():
    config_a = TenantAuthConfig(
        tenant_id=TENANT_A,
        access_token_expire_minutes=15,
        refresh_token_expire_days=3,
        session_expire_days=2,
        mfa_enabled=True,
    )
    config_b = TenantAuthConfig(
        tenant_id=TENANT_B,
        access_token_expire_minutes=60,
        refresh_token_expire_days=14,
        session_expire_days=10,
        mfa_enabled=False,
    )

    assert config_a.tenant_id != config_b.tenant_id
    assert config_a.access_token_expire_minutes != config_b.access_token_expire_minutes
    assert config_a.refresh_token_expire_days != config_b.refresh_token_expire_days
    assert config_a.session_expire_days != config_b.session_expire_days
    assert config_a.mfa_enabled is True
    assert config_b.mfa_enabled is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("access_token_expire_minutes", 0),
        ("refresh_token_expire_days", 0),
        ("session_expire_days", 0),
    ],
)
def test_tenant_config_rejects_non_positive_expiry(field, value):
    with pytest.raises(ValueError):
        TenantAuthConfig(
            tenant_id=TENANT_A,
            **{field: value},
        )


def test_tenant_config_requires_uuid_tenant_id():
    with pytest.raises(ValueError, match="tenant_id must be a valid UUID"):
        TenantAuthConfig(tenant_id="tenant-a")  # type: ignore[arg-type]


class InMemoryTenantConfigurationProvider:
    def __init__(self, configurations):
        self.configurations = configurations

    def get_auth_config(self, tenant_id):
        return self.configurations[tenant_id]


def test_provider_returns_configuration_for_requested_tenant():
    config_a = TenantAuthConfig(
        tenant_id=TENANT_A,
        access_token_expire_minutes=15,
        refresh_token_expire_days=3,
        session_expire_days=2,
        mfa_enabled=True,
    )
    config_b = TenantAuthConfig(
        tenant_id=TENANT_B,
        access_token_expire_minutes=60,
        refresh_token_expire_days=14,
        session_expire_days=10,
        mfa_enabled=False,
    )

    provider = InMemoryTenantConfigurationProvider({
        TENANT_A: config_a,
        TENANT_B: config_b,
    })

    assert provider.get_auth_config(TENANT_A) == config_a
    assert provider.get_auth_config(TENANT_B) == config_b


def test_provider_does_not_fall_back_to_another_tenant():
    provider = InMemoryTenantConfigurationProvider({
        TENANT_A: TenantAuthConfig(
            tenant_id=TENANT_A,
            access_token_expire_minutes=15,
        ),
    })

    with pytest.raises(KeyError):
        provider.get_auth_config(TENANT_B)


def test_login_applies_tenant_specific_configuration(db_session):
    from app.models.user import User
    from app.services.auth_service import hash_password, login_user

    config_a = TenantAuthConfig(
        tenant_id=TENANT_A,
        access_token_expire_minutes=15,
        refresh_token_expire_days=3,
        session_expire_days=2,
        mfa_enabled=True,
    )
    config_b = TenantAuthConfig(
        tenant_id=TENANT_B,
        access_token_expire_minutes=60,
        refresh_token_expire_days=14,
        session_expire_days=10,
        mfa_enabled=False,
    )

    provider = InMemoryTenantConfigurationProvider({
        TENANT_A: config_a,
        TENANT_B: config_b,
    })

    user_a = User(
        tenant_id=TENANT_A,
        username=f"user_a_{uuid.uuid4().hex[:8]}",
        email=f"user_a_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("Password123!"),
    )
    user_b = User(
        tenant_id=TENANT_B,
        username=f"user_b_{uuid.uuid4().hex[:8]}",
        email=f"user_b_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("Password123!"),
    )

    db_session.add_all([user_a, user_b])
    db_session.commit()

    result_a = login_user(
        db=db_session,
        email=user_a.email,
        password="Password123!",
        config_provider=provider,
    )
    result_b = login_user(
        db=db_session,
        email=user_b.email,
        password="Password123!",
        config_provider=provider,
    )

    assert result_a["access_token"] != result_b["access_token"]

    session_a = (
        db_session.query(SessionModel)
        .filter(SessionModel.user_id == user_a.id)
        .one()
    )
    session_b = (
        db_session.query(SessionModel)
        .filter(SessionModel.user_id == user_b.id)
        .one()
    )

    now = datetime.now(timezone.utc)

    session_a_expires = session_a.expires_at
    session_b_expires = session_b.expires_at

    if session_a_expires.tzinfo is None:
        session_a_expires = session_a_expires.replace(tzinfo=timezone.utc)
    if session_b_expires.tzinfo is None:
        session_b_expires = session_b_expires.replace(tzinfo=timezone.utc)

    assert 1.9 <= (session_a_expires - now).total_seconds() / 86400 <= 2.1
    assert 9.9 <= (session_b_expires - now).total_seconds() / 86400 <= 10.1


def test_default_provider_returns_safe_defaults_for_each_tenant():
    provider = DefaultTenantConfigurationProvider()

    config_a = provider.get_auth_config(TENANT_A)
    config_b = provider.get_auth_config(TENANT_B)

    assert config_a.tenant_id == TENANT_A
    assert config_b.tenant_id == TENANT_B
    assert config_a.access_token_expire_minutes == DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES
    assert config_b.access_token_expire_minutes == DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES
    assert config_a.refresh_token_expire_days == DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS
    assert config_b.refresh_token_expire_days == DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS
    assert config_a.session_expire_days == DEFAULT_SESSION_EXPIRE_DAYS
    assert config_b.session_expire_days == DEFAULT_SESSION_EXPIRE_DAYS
    assert config_a.mfa_enabled is DEFAULT_MFA_ENABLED
    assert config_b.mfa_enabled is DEFAULT_MFA_ENABLED


def test_refresh_rejects_cross_tenant_refresh_token(db_session):
    from fastapi import HTTPException
    from app.models.user import User
    from app.repositories.session_repository import create_session
    from app.repositories.refresh_token_repository import create_refresh_token
    from app.services.auth_service import hash_password, refresh_access_token
    from app.utils.jwt import create_refresh_token as create_jwt_refresh_token

    user = User(
        tenant_id=TENANT_A,
        username=f"refresh_user_{uuid.uuid4().hex[:8]}",
        email=f"refresh_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("Password123!"),
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    session = create_session(
        db=db_session,
        user_id=user.id,
        tenant_id=TENANT_A,
        session_token=uuid.uuid4().hex,
        expires_at=expires_at,
    )

    refresh_token = create_jwt_refresh_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "tenant_id": str(TENANT_B),
        },
        expires_delta=timedelta(days=7),
    )

    create_refresh_token(
        db=db_session,
        user_id=user.id,
        session_id=session.id,
        token=refresh_token,
        expires_at=expires_at,
    )
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        refresh_access_token(
            db=db_session,
            refresh_token=refresh_token,
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == "Refresh token tenant mismatch"


def test_refresh_applies_tenant_specific_access_token_configuration(db_session):
    from app.models.user import User
    from app.repositories.session_repository import create_session
    from app.repositories.refresh_token_repository import create_refresh_token
    from app.services.auth_service import hash_password, refresh_access_token
    from app.utils.jwt import create_refresh_token as create_jwt_refresh_token, decode_token

    config_a = TenantAuthConfig(
        tenant_id=TENANT_A,
        access_token_expire_minutes=15,
    )

    provider = InMemoryTenantConfigurationProvider({
        TENANT_A: config_a,
    })

    user = User(
        tenant_id=TENANT_A,
        username=f"refresh_config_{uuid.uuid4().hex[:8]}",
        email=f"refresh_config_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("Password123!"),
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    session = create_session(
        db=db_session,
        user_id=user.id,
        tenant_id=TENANT_A,
        session_token=uuid.uuid4().hex,
        expires_at=expires_at,
    )

    refresh_token = create_jwt_refresh_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "tenant_id": str(TENANT_A),
        },
        expires_delta=timedelta(days=7),
    )

    create_refresh_token(
        db=db_session,
        user_id=user.id,
        session_id=session.id,
        token=refresh_token,
        expires_at=expires_at,
    )
    db_session.commit()

    result = refresh_access_token(
        db=db_session,
        refresh_token=refresh_token,
        config_provider=provider,
    )

    payload = decode_token(result["access_token"])

    assert payload is not None
    assert payload["tenant_id"] == str(TENANT_A)

    expires_at_timestamp = payload["exp"]
    now_timestamp = datetime.now(timezone.utc).timestamp()

    assert 14.9 * 60 <= expires_at_timestamp - now_timestamp <= 15.1 * 60


def test_login_rejects_invalid_tenant_configuration(db_session):
    from app.models.user import User
    from app.services.auth_service import hash_password, login_user

    class InvalidConfigurationProvider:
        def get_auth_config(self, tenant_id):
            return TenantAuthConfig(
                tenant_id=tenant_id,
                access_token_expire_minutes=0,
            )

    user = User(
        tenant_id=TENANT_A,
        username=f"invalid_config_{uuid.uuid4().hex[:8]}",
        email=f"invalid_config_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("Password123!"),
    )

    db_session.add(user)
    db_session.commit()

    with pytest.raises(ValueError, match="access_token_expire_minutes"):
        login_user(
            db=db_session,
            email=user.email,
            password="Password123!",
            config_provider=InvalidConfigurationProvider(),
        )

    assert (
        db_session.query(SessionModel)
        .filter(SessionModel.user_id == user.id)
        .count()
        == 0
    )


def test_tenant_mfa_configuration_is_isolated():
    provider = InMemoryTenantConfigurationProvider({
        TENANT_A: TenantAuthConfig(
            tenant_id=TENANT_A,
            mfa_enabled=True,
        ),
        TENANT_B: TenantAuthConfig(
            tenant_id=TENANT_B,
            mfa_enabled=False,
        ),
    })

    config_a = provider.get_auth_config(TENANT_A)
    config_b = provider.get_auth_config(TENANT_B)

    assert config_a.mfa_enabled is True
    assert config_b.mfa_enabled is False
    assert config_a.tenant_id == TENANT_A
    assert config_b.tenant_id == TENANT_B
