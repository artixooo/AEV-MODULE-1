import unittest

from fastapi.testclient import TestClient

from app.main import app


class TestOrganizationAPIAuthentication(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_create_organization_requires_authentication(self):
        response = self.client.post(
            "/organizations",
            json={
                "organization_name": "Test Organization",
                "organization_code": "TEST-API-AUTH",
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_list_organizations_requires_authentication(self):
        response = self.client.get("/organizations")

        self.assertEqual(response.status_code, 401)

    def test_get_organization_requires_authentication(self):
        response = self.client.get(
            "/organizations/00000000-0000-0000-0000-000000000001"
        )

        self.assertEqual(response.status_code, 401)

    def test_update_organization_requires_authentication(self):
        response = self.client.patch(
            "/organizations/00000000-0000-0000-0000-000000000001",
            json={
                "organization_name": "Updated Organization",
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_delete_organization_requires_authentication(self):
        response = self.client.delete(
            "/organizations/00000000-0000-0000-0000-000000000001"
        )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()