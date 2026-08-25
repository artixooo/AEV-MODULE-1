import unittest
from datetime import datetime
import uuid

from app.models.organization import Organization
from app.schemas.organization import (
    OrganizationBase,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)


class TestModelsAndSchemas(unittest.TestCase):
    def test_organization_model_instantiation(self):
        org_id = uuid.uuid4()

        org = Organization(
            id=org_id,
            organization_name="Acme Corp",
            organization_code="ACME",
            description="Test Organization",
            website="https://acme.example.com",
            status="ACTIVE",
        )

        self.assertEqual(org.id, org_id)
        self.assertEqual(org.organization_name, "Acme Corp")
        self.assertEqual(org.organization_code, "ACME")
        self.assertEqual(org.description, "Test Organization")
        self.assertEqual(org.website, "https://acme.example.com")
        self.assertEqual(org.status, "ACTIVE")

    def test_organization_schemas(self):
        base = OrganizationBase(
            organization_name="Base Org",
            organization_code="BASE",
        )
        self.assertEqual(base.organization_name, "Base Org")
        self.assertEqual(base.organization_code, "BASE")
        self.assertEqual(base.status, "ACTIVE")

        create = OrganizationCreate(
            organization_name="Create Org",
            organization_code="CREATE",
            description="New",
            website="https://create.example.com",
        )
        self.assertEqual(create.description, "New")

        update = OrganizationUpdate(
            organization_name="Updated Name"
        )
        self.assertEqual(update.organization_name, "Updated Name")
        self.assertIsNone(update.organization_code)

        now = datetime.now()
        org_id = uuid.uuid4()

        response = OrganizationResponse(
            id=org_id,
            organization_name="Resp Org",
            organization_code="RESP",
            description="Response",
            website="https://resp.example.com",
            status="ACTIVE",
            created_at=now,
            updated_at=now,
        )

        self.assertEqual(response.id, org_id)
        self.assertEqual(response.organization_name, "Resp Org")


if __name__ == "__main__":
    unittest.main()