import logging
import hvac
from app.core.config import settings

logger = logging.getLogger("secrets_service")

class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url=settings.VAULT_ADDR,
            token=settings.VAULT_TOKEN
        )

    def is_connected(self) -> bool:
        try:
            return self.client.is_authenticated()
        except Exception as e:
            logger.error(f"Vault connection healthcheck failed: {e}")
            return False

vault_client = VaultClient()