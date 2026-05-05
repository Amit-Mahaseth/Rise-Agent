from fastapi import APIRouter

from app.api.routes import calls, dashboard, health, leads
from app.routes import router as realtime_router

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(realtime_router)
