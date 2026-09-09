from fastapi import APIRouter

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.get(
    "",
    summary="List organizations",
    description=(
        "Organization API v1 contract. "
        "Organization management implementation is outside Week 3 scope."
    ),
)
async def list_organizations():
    """
    API Contract v1 placeholder.

    Authentication and authorization will be enforced by the
    authentication-ready request handling layer.

    No organization management logic is implemented in Week 3.
    """
    return {
        "service": "organization",
        "api_version": "v1",
        "status": "contract-defined",
    }