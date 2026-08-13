"""
app/api/__init__.py

Exposes `api_router` as the single import point for the FastAPI app:

    from app.api import api_router
    app.include_router(api_router)
"""

from app.api.api import api_router

__all__: list[str] = ["api_router"]
