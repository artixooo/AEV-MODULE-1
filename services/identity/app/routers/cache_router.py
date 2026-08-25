from fastapi import APIRouter
from app.services.cache_service import cache_service

router = APIRouter(prefix="/cache", tags=["Cache Management"])


@router.post("/invalidate")
def invalidate_cache():
    """
    Explicitly invalidates all policy and permission evaluation cache entries (FR-AUTHZ-007).
    """
    cache_service.invalidate_all()
    return {"message": "Policy cache successfully invalidated", "status": "success"}
    
