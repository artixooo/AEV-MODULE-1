from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)

from app.routers.scim.dependencies import (
    get_current_tenant,
)

from app.routers.scim.errors import (
    scim_error_response,
)

from app.schemas.scim.common import (
    SCIMListResponse,
    SCIMPatchRequest,
)

from app.schemas.scim.user import (
    SCIMUserCreate,
    SCIMUserResponse,
    SCIMUserUpdate,
)

from app.services.scim.user_service import (
    SCIMUserService,
)

from app.services.scim.validation_service import (
    SCIMValidationError,
    validate_patch_operations,
)


router = APIRouter(
    prefix="/scim/v2/Users",
    tags=["SCIM Users"],
)


user_service = SCIMUserService()


@router.post(
    "",
    response_model=SCIMUserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    payload: SCIMUserCreate,
    tenant_id: str = Depends(get_current_tenant),
):
    try:
        return user_service.create_user(
            payload,
            tenant_id,
        )

    except SCIMValidationError as exc:
        return scim_error_response(
            status.HTTP_400_BAD_REQUEST,
            str(exc),
        )


@router.get(
    "",
    response_model=SCIMListResponse,
)
def list_users(
    tenant_id: str = Depends(get_current_tenant),
):
    users = user_service.list_users(
        tenant_id,
    )

    return {
        "total_results": len(users),
        "start_index": 1,
        "items_per_page": len(users),
        "resources": users,
    }


@router.get(
    "/{user_id}",
    response_model=SCIMUserResponse,
)
def get_user(
    user_id: str,
    tenant_id: str = Depends(get_current_tenant),
):
    user = user_service.get_user(
        user_id,
        tenant_id,
    )

    if user is None:
        return scim_error_response(
            status.HTTP_404_NOT_FOUND,
            "SCIM user not found.",
        )

    return user


@router.put(
    "/{user_id}",
    response_model=SCIMUserResponse,
)
def replace_user(
    user_id: str,
    payload: SCIMUserUpdate,
    tenant_id: str = Depends(get_current_tenant),
):
    try:
        user = user_service.replace_user(
            user_id,
            payload,
            tenant_id,
        )

    except SCIMValidationError as exc:
        return scim_error_response(
            status.HTTP_400_BAD_REQUEST,
            str(exc),
        )

    if user is None:
        return scim_error_response(
            status.HTTP_404_NOT_FOUND,
            "SCIM user not found.",
        )

    return user


@router.patch(
    "/{user_id}",
    response_model=SCIMUserResponse,
)
def patch_user(
    user_id: str,
    payload: SCIMPatchRequest,
    tenant_id: str = Depends(get_current_tenant),
):
    try:
        validate_patch_operations(
            payload.operations,
            resource_type="user",
        )

        user = user_service.patch_user(
            user_id,
            payload.operations,
            tenant_id,
        )

    except SCIMValidationError as exc:
        return scim_error_response(
            status.HTTP_400_BAD_REQUEST,
            str(exc),
        )

    if user is None:
        return scim_error_response(
            status.HTTP_404_NOT_FOUND,
            "SCIM user not found.",
        )

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: str,
    tenant_id: str = Depends(get_current_tenant),
):
    deleted = user_service.delete_user(
        user_id,
        tenant_id,
    )

    if not deleted:
        return scim_error_response(
            status.HTTP_404_NOT_FOUND,
            "SCIM user not found.",
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )