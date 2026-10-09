import unittest
import uuid

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.workspace import Workspace
from app.schemas.membership import MembershipCreate, MembershipUpdate
from app.services.membership import MembershipService


class TestMembershipService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.db = self.SessionLocal()
        self.service = MembershipService(self.db)

        self.organization = Organization(
            id=uuid.uuid4(),
            organization_name="Test Organization",
            organization_code=f"ORG-{uuid.uuid4().hex[:8]}",
            status="ACTIVE",
        )

        self.second_organization = Organization(
            id=uuid.uuid4(),
            organization_name="Second Organization",
            organization_code=f"ORG-{uuid.uuid4().hex[:8]}",
            status="ACTIVE",
        )

        self.db.add_all([
            self.organization,
            self.second_organization,
        ])
        self.db.commit()

        self.workspace = Workspace(
            id=uuid.uuid4(),
            organization_id=self.organization.id,
            workspace_name="Security Workspace",
            workspace_code=f"WS-{uuid.uuid4().hex[:8]}",
            status="ACTIVE",
        )

        self.second_workspace = Workspace(
            id=uuid.uuid4(),
            organization_id=self.second_organization.id,
            workspace_name="Second Workspace",
            workspace_code=f"WS-{uuid.uuid4().hex[:8]}",
            status="ACTIVE",
        )

        self.db.add_all([
            self.workspace,
            self.second_workspace,
        ])
        self.db.commit()

        self.user_id = uuid.uuid4()

    def tearDown(self):
        self.db.close()

    def test_create_membership(self):
        data = MembershipCreate(
            user_id=self.user_id,
            organization_id=self.organization.id,
            workspace_id=self.workspace.id,
        )

        membership = self.service.create_membership(data)

        self.assertIsNotNone(membership.id)
        self.assertEqual(membership.user_id, self.user_id)
        self.assertEqual(
            membership.organization_id,
            self.organization.id,
        )
        self.assertEqual(
            membership.workspace_id,
            self.workspace.id,
        )
        self.assertEqual(membership.membership_status, "ACTIVE")

    def test_create_membership_requires_existing_organization(self):
        data = MembershipCreate(
            user_id=self.user_id,
            organization_id=uuid.uuid4(),
            workspace_id=self.workspace.id,
        )

        with self.assertRaises(HTTPException) as context:
            self.service.create_membership(data)

        self.assertEqual(context.exception.status_code, 404)

    def test_create_membership_requires_existing_workspace(self):
        data = MembershipCreate(
            user_id=self.user_id,
            organization_id=self.organization.id,
            workspace_id=uuid.uuid4(),
        )

        with self.assertRaises(HTTPException) as context:
            self.service.create_membership(data)

        self.assertEqual(context.exception.status_code, 404)

    def test_workspace_must_belong_to_organization(self):
        data = MembershipCreate(
            user_id=self.user_id,
            organization_id=self.organization.id,
            workspace_id=self.second_workspace.id,
        )

        with self.assertRaises(HTTPException) as context:
            self.service.create_membership(data)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(
            context.exception.detail,
            "Workspace does not belong to the organization",
        )

    def test_duplicate_membership(self):
        data = MembershipCreate(
            user_id=self.user_id,
            organization_id=self.organization.id,
            workspace_id=self.workspace.id,
        )

        self.service.create_membership(data)

        with self.assertRaises(HTTPException) as context:
            self.service.create_membership(data)

        self.assertEqual(context.exception.status_code, 409)

    def test_same_user_can_have_different_workspace_memberships(self):
        first = MembershipCreate(
            user_id=self.user_id,
            organization_id=self.organization.id,
            workspace_id=self.workspace.id,
        )

        second_workspace = Workspace(
            id=uuid.uuid4(),
            organization_id=self.organization.id,
            workspace_name="Another Workspace",
            workspace_code=f"WS-{uuid.uuid4().hex[:8]}",
            status="ACTIVE",
        )

        self.db.add(second_workspace)
        self.db.commit()

        second = MembershipCreate(
            user_id=self.user_id,
            organization_id=self.organization.id,
            workspace_id=second_workspace.id,
        )

        membership_one = self.service.create_membership(first)
        membership_two = self.service.create_membership(second)

        self.assertNotEqual(
            membership_one.id,
            membership_two.id,
        )

    def test_get_membership_not_found(self):
        with self.assertRaises(HTTPException) as context:
            self.service.get_membership(uuid.uuid4())

        self.assertEqual(context.exception.status_code, 404)

    def test_list_memberships_by_organization(self):
        self.service.create_membership(
            MembershipCreate(
                user_id=self.user_id,
                organization_id=self.organization.id,
                workspace_id=self.workspace.id,
            )
        )

        memberships = self.service.list_memberships(
            organization_id=self.organization.id
        )

        self.assertEqual(len(memberships), 1)
        self.assertEqual(
            memberships[0].organization_id,
            self.organization.id,
        )

    def test_list_memberships_by_workspace(self):
        self.service.create_membership(
            MembershipCreate(
                user_id=self.user_id,
                organization_id=self.organization.id,
                workspace_id=self.workspace.id,
            )
        )

        memberships = self.service.list_memberships(
            workspace_id=self.workspace.id
        )

        self.assertEqual(len(memberships), 1)
        self.assertEqual(
            memberships[0].workspace_id,
            self.workspace.id,
        )

    def test_list_memberships_by_user(self):
        self.service.create_membership(
            MembershipCreate(
                user_id=self.user_id,
                organization_id=self.organization.id,
                workspace_id=self.workspace.id,
            )
        )

        memberships = self.service.list_memberships(
            user_id=self.user_id
        )

        self.assertEqual(len(memberships), 1)
        self.assertEqual(
            memberships[0].user_id,
            self.user_id,
        )

    def test_update_membership_status(self):
        membership = self.service.create_membership(
            MembershipCreate(
                user_id=self.user_id,
                organization_id=self.organization.id,
                workspace_id=self.workspace.id,
            )
        )

        updated = self.service.update_membership(
            membership.id,
            MembershipUpdate(
                membership_status="INACTIVE"
            ),
        )

        self.assertEqual(
            updated.membership_status,
            "INACTIVE",
        )

    def test_delete_membership(self):
        membership = self.service.create_membership(
            MembershipCreate(
                user_id=self.user_id,
                organization_id=self.organization.id,
                workspace_id=self.workspace.id,
            )
        )

        self.service.delete_membership(membership.id)

        with self.assertRaises(HTTPException) as context:
            self.service.get_membership(membership.id)

        self.assertEqual(context.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()