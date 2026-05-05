from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_realtime_call_service
from app.db.session import get_db
from app.repositories.lead_repository import LeadRepository

router = APIRouter()


class LeadWebhookPayload(BaseModel):
    lead_id: str
    full_name: str
    phone_number: str
    source: str = "webhook"
    product_interest: str = "personal-loan"


@router.post("/ingest")
async def ingest_lead(
    payload: LeadWebhookPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    call_service=Depends(get_realtime_call_service),
) -> dict:
    repo = LeadRepository()
    existing = repo.get(db, payload.lead_id)
    if existing:
        raise HTTPException(status_code=409, detail="Lead already exists")

    lead = repo.create(db, payload)
    call_result = await call_service.initiate_call(payload.lead_id, payload.phone_number)
    background_tasks.add_task(call_service.handle_call_session, call_result["call_id"], payload.lead_id)

    return {"lead_id": lead.lead_id, "call": call_result, "status": "accepted"}
