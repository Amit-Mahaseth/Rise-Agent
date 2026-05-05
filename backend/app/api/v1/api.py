"""
API v1 router combining all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import leads, calls, conversations, analytics, webhooks

api_router = APIRouter()
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])