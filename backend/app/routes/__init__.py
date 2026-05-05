from fastapi import APIRouter

from app.routes import call, lead, webhook

router = APIRouter()
router.include_router(lead.router, prefix="/leads", tags=["leads-v2"])
router.include_router(call.router, prefix="/calls", tags=["calls-v2"])
router.include_router(webhook.router, prefix="/webhook", tags=["webhook-v2"])
