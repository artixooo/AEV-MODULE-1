import unittest
from datetime import date, datetime
import uuid

from app.models.membership import Membership
from app.models.project import Project
from app.models.workspace import Workspace

from app.schemas.membership import (
    MembershipBase,
    MembershipCreate,
    MembershipResponse,
    MembershipUpdate,
)
from app.schemas.project import (
    ProjectBase,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.schemas.workspace import (
    WorkspaceBase,
    WorkspaceCreate,
    WorkspaceResponse,
    WorkspaceUpdate,
)


class TestWeek4ModelsAndSchemas(unittest.TestCase):

    def test_workspace_model_instantiation(self):
        organization_id = uuid.uuid4()
        workspace_id = uuid.uuid4()

        workspace = Workspace(
            id=workspace_id,
            organization_id=organization_id,
            workspace_name="Security Workspace",
            workspace_code="SEC",
            description="Security operations workspace",
            status="ACTIVE",
        )

        self.assertEqual(workspace.id, workspace_id)
        self.assertEqual(workspace.organization_id, organization_id)
        self.assertEqual(workspace.workspace_name, "Security Workspace")
        self.assertEqual(workspace.workspace_code, "SEC")
        self.assertEqual(workspace.status, "ACTIVE")

    def test_workspace_schemas(self):
        organization_id = uuid.uuid4()
        workspace_id = uuid.uuid4()
        now = datetime.now()

        base = WorkspaceBase(
            organization_id=organization_id,
            workspace_name="Base Workspace",
            workspace_code="BASE",
        )

        self.assertEqual(base.organization_id, organization_id)
        self.assertEqual(base.status, "ACTIVE")

        create = WorkspaceCreate(
            organization_id=organization_id,
            workspace_name="Create Workspace",
            workspace_code="CREATE",
            description="New workspace",
        )

        self.assertEqual(create.workspace_name, "Create Workspace")

        update = WorkspaceUpdate(
            workspace_name="Updated Workspace"
        )

        self.assertEqual(update.workspace_name, "Updated Workspace")
        self.assertIsNone(update.workspace_code)

        response = WorkspaceResponse(
            id=workspace_id,
            organization_id=organization_id,
            workspace_name="Response Workspace",
            workspace_code="RESP",
            status="ACTIVE",
            created_at=now,
            updated_at=now,
        )

        self.assertEqual(response.id, workspace_id)
        self.assertEqual(response.organization_id, organization_id)


    def test_project_model_instantiation(self):
        workspace_id = uuid.uuid4()
        project_id = uuid.uuid4()

        project = Project(
            id=project_id,
            workspace_id=workspace_id,
            project_name="SOC Automation",
            project_code="SOC-AUTO",
            description="SOC automation project",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 31),
            status="PLANNING",
        )

        self.assertEqual(project.id, project_id)
        self.assertEqual(project.workspace_id, workspace_id)
        self.assertEqual(project.project_name, "SOC Automation")
        self.assertEqual(project.project_code, "SOC-AUTO")
        self.assertEqual(project.status, "PLANNING")

    def test_project_schemas(self):
        workspace_id = uuid.uuid4()
        project_id = uuid.uuid4()
        now = datetime.now()

        base = ProjectBase(
            workspace_id=workspace_id,
            project_name="Base Project",
            project_code="BASE",
        )

        self.assertEqual(base.workspace_id, workspace_id)
        self.assertEqual(base.status, "PLANNING")

        create = ProjectCreate(
            workspace_id=workspace_id,
            project_name="Create Project",
            project_code="CREATE",
            start_date=date(2026, 9, 1),
        )

        self.assertEqual(create.project_name, "Create Project")
        self.assertEqual(create.start_date, date(2026, 9, 1))

        update = ProjectUpdate(
            project_name="Updated Project"
        )

        self.assertEqual(update.project_name, "Updated Project")
        self.assertIsNone(update.project_code)

        response = ProjectResponse(
            id=project_id,
            workspace_id=workspace_id,
            project_name="Response Project",
            project_code="RESP",
            status="PLANNING",
            created_at=now,
            updated_at=now,
        )

        self.assertEqual(response.id, project_id)
        self.assertEqual(response.workspace_id, workspace_id)


    def test_membership_model_instantiation(self):
        user_id = uuid.uuid4()
        organization_id = uuid.uuid4()
        workspace_id = uuid.uuid4()
        membership_id = uuid.uuid4()

        membership = Membership(
            id=membership_id,
            user_id=user_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            membership_status="ACTIVE",
        )

        self.assertEqual(membership.id, membership_id)
        self.assertEqual(membership.user_id, user_id)
        self.assertEqual(membership.organization_id, organization_id)
        self.assertEqual(membership.workspace_id, workspace_id)
        self.assertEqual(membership.membership_status, "ACTIVE")

    def test_membership_schemas(self):
        user_id = uuid.uuid4()
        organization_id = uuid.uuid4()
        workspace_id = uuid.uuid4()
        membership_id = uuid.uuid4()
        now = datetime.now()

        base = MembershipBase(
            user_id=user_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
        )

        self.assertEqual(base.user_id, user_id)
        self.assertEqual(base.organization_id, organization_id)
        self.assertEqual(base.workspace_id, workspace_id)
        self.assertEqual(base.membership_status, "ACTIVE")

        create = MembershipCreate(
            user_id=user_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
        )

        self.assertEqual(create.membership_status, "ACTIVE")

        update = MembershipUpdate(
            membership_status="INACTIVE"
        )

        self.assertEqual(update.membership_status, "INACTIVE")

        response = MembershipResponse(
            id=membership_id,
            user_id=user_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            membership_status="ACTIVE",
            joined_at=now,
            created_at=now,
        )

        self.assertEqual(response.id, membership_id)
        self.assertEqual(response.user_id, user_id)


if __name__ == "__main__":
    unittest.main()