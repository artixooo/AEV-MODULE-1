import unittest


class TestImports(unittest.TestCase):
    def test_imports(self):
        """Verify that all core application modules can be imported without errors."""
        import app.api
        import app.api.health
        import app.core
        import app.core.config
        import app.core.logging
        import app.db
        import app.db.database
        import app.main
        import app.models
        import app.models.organization
        import app.routers
        import app.routers.organization
        import app.schemas
        import app.schemas.organization
        import app.services
        import app.services.organization

        self.assertIsNotNone(app.main.app)
        self.assertIsNotNone(app.core.config.settings)
        self.assertIsNotNone(app.db.database.engine)
        self.assertIsNotNone(app.models.Organization)
        self.assertIsNotNone(app.schemas.OrganizationResponse)
        self.assertIsNotNone(app.routers.organization_router)
        self.assertIsNotNone(app.services.OrganizationService)


if __name__ == "__main__":
    unittest.main()
