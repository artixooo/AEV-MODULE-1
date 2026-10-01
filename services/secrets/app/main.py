import logging
from fastapi import FastAPI
from app.core.config import settings
from app.vault.client import vault_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("secrets-service")

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

@app.get("/health")
def health_check():
    logger.info("Health check probe evaluated: healthy")
    return {"status": "healthy", "service": "secrets-service"}

@app.get("/ready")
def readiness_check():
    vault_status = vault_client.is_connected()
    if vault_status:
        logger.info("Readiness check probe evaluated: Vault connected")
        return {"status": "ready", "vault": "connected"}
    
    logger.warning("Readiness check probe evaluated: Vault disconnected")
    return {"status": "unhealthy", "vault": "disconnected"}