import unittest
import uuid
from datetime import date

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.models.organization import Organization
from app.models.project import Project
from app.models.workspace import Workspace
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.project import ProjectService


class TestProjectService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.db = self.SessionLocal()
        self.service = ProjectService(self.db)

        self.organization = Organization(
            id=uuid.uuid4(),
            organization_name="Test Organization",
            organization_code=f"ORG-{uuid.uuid4().hex[:8]}",
            status="ACTIVE",
        )

        self.db.add(self.organization)
        self.db.commit()

        self.workspace = Workspace(
            id=uuid.uuid4(),
            organization_id=self.organization.id,
            workspace_name="Security Workspace",
            workspace_code=f"WS-{uuid.uuid4().hex[:8]}",
            status="ACTIVE",
        )

        self.db.add(self.workspace)
        self.db.commit()
        self.db.refresh(self.workspace)

    def tearDown(self):
        self.db.close()

    def test_create_project(self):
        data = ProjectCreate(
            workspace_id=self.workspace.id,
            project_name="SOC Automation",
            project_code="SOC-AUTO",
            description="SOC automation project",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 31),
        )

        project = self.service.create_project(data)

        self.assertIsNotNone(project.id)
        self.assertEqual(project.workspace_id, self.workspace.id)
        self.assertEqual(project.project_name, "SOC Automation")
        self.assertEqual(project.project_code, "SOC-AUTO")
        self.assertEqual(project.status, "PLANNING")

    def test_create_project_requires_existing_workspace(self):
        data = ProjectCreate(
            workspace_id=uuid.uuid4(),
            project_name="Invalid Project",
            project_code="INVALID",
        )

        with self.assertRaises(HTTPException) as context:
            self.service.create_project(data)

        self.assertEqual(context.exception.status_code, 404)

    def test_duplicate_project_code_same_workspace(self):
        first = ProjectCreate(
            workspace_id=self.workspace.id,
            project_name="First Project",
            project_code="DUPLICATE",
        )

        self.service.create_project(first)

        second = ProjectCreate(
            workspace_id=self.workspace.id,
            project_name="Second Project",
            project_code="DUPLICATE",
        )

        with self.assertRaises(HTTPException) as context:
            self.service.create_project(second)

        self.assertEqual(context.exception.status_code, 409)

    def test_same_project_code_allowed_in_different_workspaces(self):
        second_workspace = Workspace(
            id=uuid.uuid4(),
            organization_id=self.organization.id,
            workspace_name="Second Workspace",
            workspace_code=f"WS-{uuid.uuid4().hex[:8]}",
            status="ACTIVE",
        )

        self.db.add(second_workspace)
        self.db.commit()

        first = ProjectCreate(
            workspace_id=self.workspace.id,
            project_name="Project One",
            project_code="COMMON",
        )

        second = ProjectCreate(
            workspace_id=second_workspace.id,
            project_name="Project Two",
            project_code="COMMON",
        )

        project_one = self.service.create_project(first)
        project_two = self.service.create_project(second)

        self.assertEqual(project_one.project_code, "COMMON")
        self.assertEqual(project_two.project_code, "COMMON")
        self.assertNotEqual(
            project_one.workspace_id,
            project_two.workspace_id,
        )

    def test_invalid_project_dates(self):
        data = ProjectCreate(
            workspace_id=self.workspace.id,
            project_name="Invalid Dates",
            project_code="BAD-DATE",
            start_date=date(2026, 12, 31),
            end_date=date(2026, 9, 1),
        )

        with self.assertRaises(HTTPException) as context:
            self.service.create_project(data)

        self.assertEqual(context.exception.status_code, 400)

    def test_get_project_not_found(self):
        with self.assertRaises(HTTPException) as context:
            self.service.get_project(uuid.uuid4())

        self.assertEqual(context.exception.status_code, 404)

    def test_list_projects_by_workspace(self):
        self.service.create_project(
            ProjectCreate(
                workspace_id=self.workspace.id,
                project_name="Project A",
                project_code="A",
            )
        )

        self.service.create_project(
            ProjectCreate(
                workspace_id=self.workspace.id,
                project_name="Project B",
                project_code="B",
            )
        )

        projects = self.service.list_projects(
            workspace_id=self.workspace.id
        )

        self.assertEqual(len(projects), 2)
        self.assertEqual(
            [project.project_code for project in projects],
            ["A", "B"],
        )

    def test_update_project(self):
        project = self.service.create_project(
            ProjectCreate(
                workspace_id=self.workspace.id,
                project_name="Original Project",
                project_code="ORIGINAL",
            )
        )

        updated = self.service.update_project(
            project.id,
            ProjectUpdate(
                project_name="Updated Project",
            ),
        )

        self.assertEqual(updated.project_name, "Updated Project")
        self.assertEqual(updated.project_code, "ORIGINAL")
        self.assertEqual(
            updated.workspace_id,
            self.workspace.id,
        )

    def test_update_duplicate_project_code(self):
        self.service.create_project(
            ProjectCreate(
                workspace_id=self.workspace.id,
                project_name="Project One",
                project_code="ONE",
            )
        )

        project_two = self.service.create_project(
            ProjectCreate(
                workspace_id=self.workspace.id,
                project_name="Project Two",
                project_code="TWO",
            )
        )

        with self.assertRaises(HTTPException) as context:
            self.service.update_project(
                project_two.id,
                ProjectUpdate(project_code="ONE"),
            )

        self.assertEqual(context.exception.status_code, 409)

    def test_update_invalid_project_dates(self):
        project = self.service.create_project(
            ProjectCreate(
                workspace_id=self.workspace.id,
                project_name="Date Project",
                project_code="DATES",
                start_date=date(2026, 9, 1),
                end_date=date(2026, 12, 31),
            )
        )

        with self.assertRaises(HTTPException) as context:
            self.service.update_project(
                project.id,
                ProjectUpdate(
                    start_date=date(2026, 12, 31),
                    end_date=date(2026, 9, 1),
                ),
            )

        self.assertEqual(context.exception.status_code, 400)

    def test_delete_project(self):
        project = self.service.create_project(
            ProjectCreate(
                workspace_id=self.workspace.id,
                project_name="Delete Me",
                project_code="DELETE",
            )
        )

        self.service.delete_project(project.id)

        with self.assertRaises(HTTPException) as context:
            self.service.get_project(project.id)

        self.assertEqual(context.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()