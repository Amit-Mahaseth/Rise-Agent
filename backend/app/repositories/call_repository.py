from collections import Counter

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.call import CallRecord
from app.models.lead import Lead
from app.utils.time import utcnow


class CallRepository:
    def create(self, db: Session, lead_id: str, status: str = "queued") -> CallRecord:
        call = CallRecord(lead_id=lead_id, status=status)
        db.add(call)
        db.commit()
        db.refresh(call)
        return call

    def get(self, db: Session, call_id: str) -> CallRecord | None:
        return db.get(CallRecord, call_id)

    def get_by_provider_call_id(self, db: Session, provider_call_id: str) -> CallRecord | None:
        stmt = select(CallRecord).where(CallRecord.provider_call_id == provider_call_id)
        return db.scalar(stmt)

    def update(self, db: Session, call: CallRecord) -> CallRecord:
        db.add(call)
        db.commit()
        db.refresh(call)
        return call

    def append_transcript(self, db: Session, call: CallRecord, speaker: str, text: str) -> CallRecord:
        prefix = f"{speaker}: {text}".strip()
        call.transcript = f"{call.transcript}\n{prefix}".strip()
        call.updated_at = utcnow()
        return self.update(db, call)

    def get_funnel_metrics(self, db: Session) -> dict:
        total = db.scalar(select(func.count()).select_from(Lead)) or 0
        hot = db.scalar(select(func.count()).select_from(Lead).where(Lead.classification == "HOT")) or 0
        warm = db.scalar(select(func.count()).select_from(Lead).where(Lead.classification == "WARM")) or 0
        cold = db.scalar(select(func.count()).select_from(Lead).where(Lead.classification == "COLD")) or 0

        return {
            "total_leads": total,
            "hot": hot,
            "warm": warm,
            "cold": cold,
            "hot_rate": round((hot / total) * 100, 2) if total else 0.0,
        }

    def get_recent_summaries(self, db: Session, limit: int = 10) -> list[dict]:
        stmt = (
            select(CallRecord, Lead.full_name, Lead.status, Lead.score)
            .join(Lead, Lead.lead_id == CallRecord.lead_id)
            .order_by(desc(CallRecord.updated_at))
            .limit(limit)
        )
        rows = db.execute(stmt).all()
        items: list[dict] = []
        for call, full_name, lead_status, lead_score in rows:
            items.append(
                {
                    "call_id": call.id,
                    "lead_id": call.lead_id,
                    "customer_name": full_name,
                    "lead_status": lead_status,
                    "lead_score": lead_score,
                    "classification": call.classification,
                    "language": call.detected_language,
                    "intent": call.intent,
                    "next_action": call.next_action,
                    "summary": call.summary,
                    "duration_seconds": call.duration_seconds,
                }
            )
        return items

    def get_rm_tracking(self, db: Session) -> list[dict]:
        leads = db.scalars(select(Lead)).all()
        rm_counter: dict[str, Counter] = {}

        for lead in leads:
            rm_name = lead.assigned_rm or "Unassigned"
            rm_counter.setdefault(rm_name, Counter())
            rm_counter[rm_name]["assigned_leads"] += 1
            if lead.classification == "HOT":
                rm_counter[rm_name]["hot_leads"] += 1
            if lead.classification == "WARM":
                rm_counter[rm_name]["warm_leads"] += 1

        return [
            {
                "rm_name": rm_name,
                "assigned_leads": counts["assigned_leads"],
                "hot_leads": counts["hot_leads"],
                "warm_leads": counts["warm_leads"],
            }
            for rm_name, counts in sorted(rm_counter.items())
        ]

    def get_language_distribution(self, db: Session) -> dict[str, int]:
        rows = db.execute(select(CallRecord.detected_language)).all()
        counter = Counter(row[0] or "Unknown" for row in rows)
        return dict(counter)
