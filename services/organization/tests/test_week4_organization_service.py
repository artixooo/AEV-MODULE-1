import unittest
import uuid

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.models.organization import Organization
from app.models.membership import Membership
from app.models.workspace import Workspace
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.core.context import TenantContext
from app.services.organization import OrganizationService


class TestOrganizationService(unittest.TestCase):

    def setUp(self):
        # Create a completely fresh in-memory database for every test.
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

        self.db = self.SessionLocal()

        self.context = TenantContext(
            user_id="00000000-0000-0000-0000-000000000001",
            tenant_id="tenant-test-001",
        )

        self.service = OrganizationService(self.db, self.context)

    def _create_test_organization(self, data):
        organization = self.service.create_organization(data)
        self.add_membership(organization.id)
        return organization

    def add_membership(self, organization_id):
        workspace = Workspace(
            organization_id=organization_id,
            workspace_name="Test Workspace",
            workspace_code=f"WS-{uuid.uuid4().hex[:8]}",
            status="ACTIVE",
        )

        self.db.add(workspace)
        self.db.commit()
        self.db.refresh(workspace)

        membership = Membership(
            user_id=uuid.UUID(self.context.user_id),
            organization_id=organization_id,
            workspace_id=workspace.id,
            membership_status="ACTIVE",
        )

        self.db.add(membership)
        self.db.commit()

        return membership
    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_get_status(self):
        result = self.service.get_status()

        self.assertEqual(
            result,
            {"status": "OrganizationService initialized"},
        )

    def test_create_organization(self):
        data = OrganizationCreate(
            organization_name="Acme Corporation",
            organization_code="ACME",
            description="Test organization",
            website="https://acme.example.com",
        )

        organization = self.service.create_organization(data)

        self.assertIsNotNone(organization.id)
        self.assertEqual(
            organization.organization_name,
            "Acme Corporation",
        )
        self.assertEqual(
            organization.organization_code,
            "ACME",
        )
        self.assertEqual(
            organization.description,
            "Test organization",
        )
        self.assertEqual(
            organization.website,
            "https://acme.example.com",
        )
        self.assertEqual(
            organization.status,
            "ACTIVE",
        )
        self.assertIsNone(
            organization.parent_organization_id,
        )

    def test_duplicate_organization_code(self):
        first = OrganizationCreate(
            organization_name="First Organization",
            organization_code="DUPLICATE",
        )

        self._create_test_organization(first)

        second = OrganizationCreate(
            organization_name="Second Organization",
            organization_code="DUPLICATE",
        )

        with self.assertRaises(HTTPException) as context:
            self._create_test_organization(second)

        self.assertEqual(
            context.exception.status_code,
            409,
        )
        self.assertEqual(
            context.exception.detail,
            "Organization code already exists",
        )

    def test_create_organization_with_existing_parent(self):
        parent = self._create_test_organization(
            OrganizationCreate(
                organization_name="Parent Organization",
                organization_code="PARENT",
            )
        )

        child = self._create_test_organization(
            OrganizationCreate(
                organization_name="Child Organization",
                organization_code="CHILD",
                parent_organization_id=parent.id,
            )
        )

        self.assertEqual(
            child.parent_organization_id,
            parent.id,
        )

    def test_create_organization_requires_existing_parent(self):
        data = OrganizationCreate(
            organization_name="Child Organization",
            organization_code="CHILD",
            parent_organization_id=uuid.uuid4(),
        )

        with self.assertRaises(HTTPException) as context:
            self._create_test_organization(data)

        self.assertEqual(
            context.exception.status_code,
            404,
        )
        self.assertEqual(
            context.exception.detail,
            "Parent organization not found",
        )

    def test_get_organization(self):
        created = self._create_test_organization(
            OrganizationCreate(
                organization_name="Test Organization",
                organization_code="TEST",
            )
        )

        organization = self.service.get_organization(
            created.id
        )

        self.assertEqual(
            organization.id,
            created.id,
        )
        self.assertEqual(
            organization.organization_name,
            "Test Organization",
        )
        self.assertEqual(
            organization.organization_code,
            "TEST",
        )

    def test_get_organization_not_found(self):
        with self.assertRaises(HTTPException) as context:
            self.service.get_organization(uuid.uuid4())

        self.assertEqual(
            context.exception.status_code,
            404,
        )
        self.assertEqual(
            context.exception.detail,
            "Organization not found",
        )

    def test_list_organizations(self):
        self._create_test_organization(
            OrganizationCreate(
                organization_name="Organization B",
                organization_code="ORG-B",
            )
        )

        self._create_test_organization(
            OrganizationCreate(
                organization_name="Organization A",
                organization_code="ORG-A",
            )
        )

        organizations = self.service.list_organizations()

        self.assertEqual(
            len(organizations),
            2,
        )

        self.assertEqual(
            [org.organization_name for org in organizations],
            [
                "Organization A",
                "Organization B",
            ],
        )

    def test_list_organizations_by_parent(self):
        parent = self._create_test_organization(
            OrganizationCreate(
                organization_name="Parent",
                organization_code="PARENT",
            )
        )

        self._create_test_organization(
            OrganizationCreate(
                organization_name="Child One",
                organization_code="CHILD-1",
                parent_organization_id=parent.id,
            )
        )

        self._create_test_organization(
            OrganizationCreate(
                organization_name="Child Two",
                organization_code="CHILD-2",
                parent_organization_id=parent.id,
            )
        )

        self._create_test_organization(
            OrganizationCreate(
                organization_name="Unrelated",
                organization_code="UNRELATED",
            )
        )

        organizations = self.service.list_organizations(
            parent_organization_id=parent.id
        )

        self.assertEqual(
            len(organizations),
            2,
        )

        self.assertEqual(
            {org.organization_code for org in organizations},
            {
                "CHILD-1",
                "CHILD-2",
            },
        )

    def test_update_organization(self):
        organization = self._create_test_organization(
            OrganizationCreate(
                organization_name="Original Name",
                organization_code="ORIGINAL",
            )
        )

        updated = self.service.update_organization(
            organization.id,
            OrganizationUpdate(
                organization_name="Updated Name",
            ),
        )

        self.assertEqual(
            updated.organization_name,
            "Updated Name",
        )
        self.assertEqual(
            updated.organization_code,
            "ORIGINAL",
        )

    def test_update_duplicate_organization_code(self):
        first = self._create_test_organization(
            OrganizationCreate(
                organization_name="First",
                organization_code="FIRST",
            )
        )

        second = self._create_test_organization(
            OrganizationCreate(
                organization_name="Second",
                organization_code="SECOND",
            )
        )

        with self.assertRaises(HTTPException) as context:
            self.service.update_organization(
                second.id,
                OrganizationUpdate(
                    organization_code=first.organization_code,
                ),
            )

        self.assertEqual(
            context.exception.status_code,
            409,
        )
        self.assertEqual(
            context.exception.detail,
            "Organization code already exists",
        )

    def test_update_parent_organization(self):
        parent = self._create_test_organization(
            OrganizationCreate(
                organization_name="Parent",
                organization_code="PARENT",
            )
        )

        child = self._create_test_organization(
            OrganizationCreate(
                organization_name="Child",
                organization_code="CHILD",
            )
        )

        updated = self.service.update_organization(
            child.id,
            OrganizationUpdate(
                parent_organization_id=parent.id,
            ),
        )

        self.assertEqual(
            updated.parent_organization_id,
            parent.id,
        )

    def test_update_self_parent_rejected(self):
        organization = self._create_test_organization(
            OrganizationCreate(
                organization_name="Organization",
                organization_code="ORG",
            )
        )

        with self.assertRaises(HTTPException) as context:
            self.service.update_organization(
                organization.id,
                OrganizationUpdate(
                    parent_organization_id=organization.id,
                ),
            )

        self.assertEqual(
            context.exception.status_code,
            400,
        )
        self.assertEqual(
            context.exception.detail,
            "Organization cannot be its own parent",
        )

    def test_update_missing_parent_rejected(self):
        organization = self._create_test_organization(
            OrganizationCreate(
                organization_name="Organization",
                organization_code="ORG",
            )
        )

        with self.assertRaises(HTTPException) as context:
            self.service.update_organization(
                organization.id,
                OrganizationUpdate(
                    parent_organization_id=uuid.uuid4(),
                ),
            )

        self.assertEqual(
            context.exception.status_code,
            404,
        )
        self.assertEqual(
            context.exception.detail,
            "Parent organization not found",
        )

    def test_delete_organization(self):
        organization = self._create_test_organization(
            OrganizationCreate(
                organization_name="Delete Me",
                organization_code="DELETE",
            )
        )

        self.service.delete_organization(
            organization.id
        )

        with self.assertRaises(HTTPException) as context:
            self.service.get_organization(
                organization.id
            )

        self.assertEqual(
            context.exception.status_code,
            404,
        )


if __name__ == "__main__":
    unittest.main()















