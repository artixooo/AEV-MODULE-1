import pytest
from pydantic import ValidationError

from app.schemas.scim.config import SCIMConfigurationCreate


def test_valid_scim_configuration():
    config = SCIMConfigurationCreate(
        tenant_id="tenant-001",
        enabled=True,
        endpoint="/scim/v2",
        provisioning_enabled=True,
        status="active",
    )

    assert config.tenant_id == "tenant-001"
    assert config.enabled is True
    assert config.endpoint == "/scim/v2"
    assert config.provisioning_enabled is True
    assert config.status == "active"


def test_scim_configuration_requires_tenant_id():
    with pytest.raises(ValidationError):
        SCIMConfigurationCreate(
            tenant_id="",
            endpoint="/scim/v2",
        )


def test_scim_configuration_rejects_invalid_endpoint():
    with pytest.raises(ValidationError):
        SCIMConfigurationCreate(
            tenant_id="tenant-001",
            endpoint="invalid-endpoint",
        )


def test_scim_configuration_rejects_non_scim_endpoint():
    with pytest.raises(ValidationError):
        SCIMConfigurationCreate(
            tenant_id="tenant-001",
            endpoint="/api/v1",
        )


def test_scim_configuration_rejects_invalid_status():
    with pytest.raises(ValidationError):
        SCIMConfigurationCreate(
            tenant_id="tenant-001",
            status="invalid",
        )


def test_scim_configuration_can_be_disabled():
    config = SCIMConfigurationCreate(
        tenant_id="tenant-001",
        enabled=False,
        provisioning_enabled=False,
        status="disabled",
    )

    assert config.enabled is False
    assert config.provisioning_enabled is False
    assert config.status == "disabled"