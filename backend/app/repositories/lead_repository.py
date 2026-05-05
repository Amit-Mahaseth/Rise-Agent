from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.schemas.lead import LeadCreate


class LeadRepository:
    def create(self, db: Session, payload: LeadCreate) -> Lead:
        lead = Lead(**payload.model_dump())
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return lead

    def get(self, db: Session, lead_id: str) -> Lead | None:
        stmt = select(Lead).where(Lead.lead_id == lead_id)
        return db.scalar(stmt)

    def update(self, db: Session, lead: Lead) -> Lead:
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return lead
