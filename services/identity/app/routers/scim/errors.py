from __future__ import annotations

from fastapi.responses import JSONResponse

from app.schemas.scim.common import SCIMErrorResponse


def scim_error_response(
    status_code: int,
    detail: str,
) -> JSONResponse:
    error = SCIMErrorResponse(
        detail=detail,
        status=str(status_code),
    )

    return JSONResponse(
        status_code=status_code,
        content=error.model_dump(),
    ) 