from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_orchestrator
from app.db.session import get_db
from app.schemas.lead import LeadCreate, LeadCreateResponse

router = APIRouter()


@router.post("", response_model=LeadCreateResponse, status_code=202)
def create_lead(
    payload: LeadCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    orchestrator=Depends(get_orchestrator),
) -> LeadCreateResponse:
    return orchestrator.register_lead(db, payload, background_tasks)
