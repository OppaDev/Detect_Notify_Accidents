# app/api/endpoints/__init__.py
from app.api.endpoints.stream import router as stream_router
from app.api.endpoints.notifications import router as notifications_router

__all__ = ["stream_router", "notifications_router"]
