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

from app.schemas.scim.group import (
    SCIMGroupCreate,
    SCIMGroupResponse,
    SCIMGroupUpdate,
)

from app.services.scim.group_service import (
    SCIMGroupService,
)

from app.services.scim.validation_service import (
    SCIMValidationError,
    validate_patch_operations,
)


router = APIRouter(
    prefix="/scim/v2/Groups",
    tags=["SCIM Groups"],
)


group_service = SCIMGroupService()


@router.post(
    "",
    response_model=SCIMGroupResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_group(
    payload: SCIMGroupCreate,
    tenant_id: str = Depends(get_current_tenant),
):
    try:
        return group_service.create_group(
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
def list_groups(
    tenant_id: str = Depends(get_current_tenant),
):
    groups = group_service.list_groups(
        tenant_id,
    )

    return {
        "total_results": len(groups),
        "start_index": 1,
        "items_per_page": len(groups),
        "resources": groups,
    }


@router.get(
    "/{group_id}",
    response_model=SCIMGroupResponse,
)
def get_group(
    group_id: str,
    tenant_id: str = Depends(get_current_tenant),
):
    group = group_service.get_group(
        group_id,
        tenant_id,
    )

    if group is None:
        return scim_error_response(
            status.HTTP_404_NOT_FOUND,
            "SCIM group not found.",
        )

    return group


@router.put(
    "/{group_id}",
    response_model=SCIMGroupResponse,
)
def replace_group(
    group_id: str,
    payload: SCIMGroupUpdate,
    tenant_id: str = Depends(get_current_tenant),
):
    try:
        group = group_service.replace_group(
            group_id,
            payload,
            tenant_id,
        )

    except SCIMValidationError as exc:
        return scim_error_response(
            status.HTTP_400_BAD_REQUEST,
            str(exc),
        )

    if group is None:
        return scim_error_response(
            status.HTTP_404_NOT_FOUND,
            "SCIM group not found.",
        )

    return group


@router.patch(
    "/{group_id}",
    response_model=SCIMGroupResponse,
)
def patch_group(
    group_id: str,
    payload: SCIMPatchRequest,
    tenant_id: str = Depends(get_current_tenant),
):
    try:
        validate_patch_operations(
            payload.operations,
            resource_type="group",
        )

        group = group_service.patch_group(
            group_id,
            payload.operations,
            tenant_id,
        )

    except SCIMValidationError as exc:
        return scim_error_response(
            status.HTTP_400_BAD_REQUEST,
            str(exc),
        )

    if group is None:
        return scim_error_response(
            status.HTTP_404_NOT_FOUND,
            "SCIM group not found.",
        )

    return group


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_group(
    group_id: str,
    tenant_id: str = Depends(get_current_tenant),
):
    deleted = group_service.delete_group(
        group_id,
        tenant_id,
    )

    if not deleted:
        return scim_error_response(
            status.HTTP_404_NOT_FOUND,
            "SCIM group not found.",
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )