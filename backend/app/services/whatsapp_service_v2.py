from app.models.lead import Lead
from app.services.messaging.whatsapp import WhatsAppService


class WhatsAppTemplateService:
    def __init__(self, client: WhatsAppService) -> None:
        self._client = client

    async def send_template_message(self, phone: str, template_id: str, variables: dict[str, str]) -> dict:
        message = template_id.format(**variables) if "{" in template_id else template_id
        lead = Lead(lead_id="temp", full_name=variables.get("name", "Lead"), phone_number=phone)
        result = self._client.send_warm_followup(lead=lead, summary=message)
        return result

    async def send_warm_personalized_followup(
        self,
        *,
        phone: str,
        customer_name: str,
        summary: str | None,
        objections: list[str] | None = None,
        intent: str | None = None,
        language: str | None = None,
    ) -> dict:
        """
        Personalized WhatsApp follow-up with conversation-specific context.
        Uses the existing Twilio-backed WhatsAppService.
        """
        top_objection = (objections or [])[:1]
        objection_hint = top_objection[0] if top_objection else None

        # Keep this short: WhatsApp + voice follow-up needs to be snappy.
        personalized_summary = summary or ""
        if objection_hint:
            personalized_summary = f"You mentioned '{objection_hint}'. {personalized_summary}".strip()

        if intent and not personalized_summary:
            personalized_summary = f"Your intent looks {intent}. We'll share next steps."

        lead = Lead(lead_id="temp", full_name=customer_name, phone_number=phone, preferred_language=language)
        return self._client.send_warm_followup(lead=lead, summary=personalized_summary)
