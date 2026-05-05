from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.call_repository import CallRepository
from app.schemas.dashboard import DashboardResponse

router = APIRouter()
call_repository = CallRepository()


@router.get("/summary", response_model=DashboardResponse)
def get_dashboard_summary(db: Session = Depends(get_db)) -> DashboardResponse:
    return DashboardResponse(
        funnel=call_repository.get_funnel_metrics(db),
        call_summaries=call_repository.get_recent_summaries(db),
        rm_tracking=call_repository.get_rm_tracking(db),
        language_distribution=call_repository.get_language_distribution(db),
    )

