import unittest
from app.core.config import Settings, settings


class TestConfig(unittest.TestCase):
    def test_config_loading(self):
        self.assertEqual(settings.APP_NAME, "Organization Service")
        self.assertEqual(settings.PORT, 8001)
        self.assertIn("postgresql://", settings.DATABASE_URL)

    def test_custom_settings_instantiation(self):
        custom_settings = Settings(APP_NAME="Test Service", PORT=9000)
        self.assertEqual(custom_settings.APP_NAME, "Test Service")
        self.assertEqual(custom_settings.PORT, 9000)


if __name__ == "__main__":
    unittest.main()
