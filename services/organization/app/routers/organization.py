from fastapi import APIRouter

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("")
@router.get("/")
async def list_organizations():
    """Stub endpoint for listing organizations (Week 2 preparation)."""
    return {"message": "Organization router prepared for Week 2"}
