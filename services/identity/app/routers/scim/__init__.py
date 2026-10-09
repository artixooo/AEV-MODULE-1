from app.routers.scim.groups import (
    router as groups_router,
)

from app.routers.scim.users import (
    router as users_router,
)


__all__ = [
    "users_router",
    "groups_router",
]
    
