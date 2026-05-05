import logging

import httpx

from app.core.config import Settings
from app.models.call import CallRecord
from app.models.lead import Lead

logger = logging.getLogger(__name__)

DEFAULT_RM_BY_LANGUAGE = {
    "Hindi": "RM North Desk",
    "Hinglish": "RM North Desk",
    "English": "RM Prime Desk",
    "Marathi": "RM West Desk",
    "Gujarati": "RM West Desk",
    "Tamil": "RM South Desk",
    "Telugu": "RM South Desk",
    "Bengali": "RM East Desk",
}


class HumanHandoffService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def assign_rm(self, lead: Lead, call: CallRecord) -> str:
        return lead.assigned_rm or DEFAULT_RM_BY_LANGUAGE.get(call.detected_language or "English", "RM Prime Desk")

    def notify(self, lead: Lead, call: CallRecord) -> dict:
        rm_name = self.assign_rm(lead, call)
        payload = {
            "lead_id": lead.lead_id,
            "lead_name": lead.full_name,
            "rm_name": rm_name,
            "phone_number": lead.phone_number,
            "classification": call.classification,
            "score_breakdown": call.score_breakdown,
            "summary": call.summary,
            "transcript": call.transcript,
        }

        if not self.settings.rm_handoff_webhook:
            logger.info("RM handoff webhook not configured. Simulating handoff for %s", lead.lead_id)
            return {"status": "simulated", "rm_name": rm_name, "payload": payload}

        response = httpx.post(self.settings.rm_handoff_webhook, json=payload, timeout=15.0)
        response.raise_for_status()
        return {"status": "sent", "rm_name": rm_name}

