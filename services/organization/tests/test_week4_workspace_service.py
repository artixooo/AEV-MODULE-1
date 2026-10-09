import unittest
import uuid

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.models.organization import Organization
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate
from app.services.workspace import WorkspaceService


class TestWorkspaceService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.db = self.SessionLocal()
        self.service = WorkspaceService(self.db)

        self.organization = Organization(
            id=uuid.uuid4(),
            organization_name="Test Organization",
            organization_code=f"ORG-{uuid.uuid4().hex[:8]}",
            status="ACTIVE",
        )

        self.db.add(self.organization)
        self.db.commit()
        self.db.refresh(self.organization)

    def tearDown(self):
        self.db.close()

    def test_create_workspace(self):
        data = WorkspaceCreate(
            organization_id=self.organization.id,
            workspace_name="Security Workspace",
            workspace_code="SEC",
        )

        workspace = self.service.create_workspace(data)

        self.assertIsNotNone(workspace.id)
        self.assertEqual(workspace.organization_id, self.organization.id)
        self.assertEqual(workspace.workspace_name, "Security Workspace")
        self.assertEqual(workspace.workspace_code, "SEC")

    def test_create_workspace_requires_existing_organization(self):
        data = WorkspaceCreate(
            organization_id=uuid.uuid4(),
            workspace_name="Invalid Workspace",
            workspace_code="INVALID",
        )

        with self.assertRaises(HTTPException) as context:
            self.service.create_workspace(data)

        self.assertEqual(context.exception.status_code, 404)

    def test_duplicate_workspace_code_same_organization(self):
        first = WorkspaceCreate(
            organization_id=self.organization.id,
            workspace_name="First Workspace",
            workspace_code="DUPLICATE",
        )

        self.service.create_workspace(first)

        second = WorkspaceCreate(
            organization_id=self.organization.id,
            workspace_name="Second Workspace",
            workspace_code="DUPLICATE",
        )

        with self.assertRaises(HTTPException) as context:
            self.service.create_workspace(second)

        self.assertEqual(context.exception.status_code, 409)

    def test_same_workspace_code_allowed_in_different_organizations(self):
        second_org = Organization(
            id=uuid.uuid4(),
            organization_name="Second Organization",
            organization_code=f"ORG-{uuid.uuid4().hex[:8]}",
            status="ACTIVE",
        )

        self.db.add(second_org)
        self.db.commit()

        first = WorkspaceCreate(
            organization_id=self.organization.id,
            workspace_name="Workspace One",
            workspace_code="COMMON",
        )

        second = WorkspaceCreate(
            organization_id=second_org.id,
            workspace_name="Workspace Two",
            workspace_code="COMMON",
        )

        workspace_one = self.service.create_workspace(first)
        workspace_two = self.service.create_workspace(second)

        self.assertEqual(workspace_one.workspace_code, "COMMON")
        self.assertEqual(workspace_two.workspace_code, "COMMON")
        self.assertNotEqual(
            workspace_one.organization_id,
            workspace_two.organization_id,
        )

    def test_get_workspace_not_found(self):
        with self.assertRaises(HTTPException) as context:
            self.service.get_workspace(uuid.uuid4())

        self.assertEqual(context.exception.status_code, 404)

    def test_list_workspaces_by_organization(self):
        self.service.create_workspace(
            WorkspaceCreate(
                organization_id=self.organization.id,
                workspace_name="Workspace A",
                workspace_code="A",
            )
        )

        self.service.create_workspace(
            WorkspaceCreate(
                organization_id=self.organization.id,
                workspace_name="Workspace B",
                workspace_code="B",
            )
        )

        workspaces = self.service.list_workspaces(
            organization_id=self.organization.id
        )

        self.assertEqual(len(workspaces), 2)
        self.assertEqual(
            [workspace.workspace_code for workspace in workspaces],
            ["A", "B"],
        )

    def test_update_workspace(self):
        workspace = self.service.create_workspace(
            WorkspaceCreate(
                organization_id=self.organization.id,
                workspace_name="Original Workspace",
                workspace_code="ORIGINAL",
            )
        )

        updated = self.service.update_workspace(
            workspace.id,
            WorkspaceUpdate(
                workspace_name="Updated Workspace",
            ),
        )

        self.assertEqual(updated.workspace_name, "Updated Workspace")
        self.assertEqual(updated.workspace_code, "ORIGINAL")
        self.assertEqual(
            updated.organization_id,
            self.organization.id,
        )

    def test_update_duplicate_workspace_code(self):
        self.service.create_workspace(
            WorkspaceCreate(
                organization_id=self.organization.id,
                workspace_name="Workspace One",
                workspace_code="ONE",
            )
        )

        workspace_two = self.service.create_workspace(
            WorkspaceCreate(
                organization_id=self.organization.id,
                workspace_name="Workspace Two",
                workspace_code="TWO",
            )
        )

        with self.assertRaises(HTTPException) as context:
            self.service.update_workspace(
                workspace_two.id,
                WorkspaceUpdate(workspace_code="ONE"),
            )

        self.assertEqual(context.exception.status_code, 409)

    def test_delete_workspace(self):
        workspace = self.service.create_workspace(
            WorkspaceCreate(
                organization_id=self.organization.id,
                workspace_name="Delete Me",
                workspace_code="DELETE",
            )
        )

        self.service.delete_workspace(workspace.id)

        with self.assertRaises(HTTPException) as context:
            self.service.get_workspace(workspace.id)

        self.assertEqual(context.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()