from app.core.context import TenantContext, build_tenant_context


def test_build_tenant_context_with_tenant():
    claims = {
        "sub": "user-123",
        "tenant_id": "tenant-456",
    }

    context = build_tenant_context(claims)

    assert context.user_id == "user-123"
    assert context.tenant_id == "tenant-456"
    assert context.is_tenant_available() is True


def test_build_tenant_context_without_tenant():
    claims = {
        "sub": "user-123",
    }

    context = build_tenant_context(claims)

    assert context.user_id == "user-123"
    assert context.tenant_id is None
    assert context.is_tenant_available() is False


def test_build_tenant_context_requires_subject():
    claims = {
        "tenant_id": "tenant-456",
    }

    try:
        build_tenant_context(claims)
        assert False
    except ValueError as exc:
        assert str(exc) == "JWT subject claim is required"