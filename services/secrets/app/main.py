from fastapi import FastAPI
from app.core.config import settings
from app.vault.client import vault_client

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "secrets-service"}

@app.get("/ready")
def readiness_check():
    vault_status = vault_client.is_connected()
    if vault_status:
        return {"status": "ready", "vault": "connected"}
    return {"status": "unhealthy", "vault": "disconnected"}
