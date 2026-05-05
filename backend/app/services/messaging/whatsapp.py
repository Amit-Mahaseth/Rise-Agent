import logging

from app.core.config import Settings
from app.models.lead import Lead

logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = None
        if settings.twilio_account_sid and settings.twilio_auth_token:
            try:
                from twilio.rest import Client

                self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
            except ModuleNotFoundError:
                logger.warning("Twilio SDK not installed. WhatsApp will stay in simulation mode.")

    def send_warm_followup(self, lead: Lead, summary: str | None) -> dict:
        body = (
            f"Hi {lead.full_name}, this is Rupeezy. "
            f"Thanks for speaking with us. Here's your application link: {self.settings.warm_followup_url}. "
            f"Summary: {summary or 'Our team is ready to help you continue the application.'}"
        )

        if not self.client:
            logger.info("WhatsApp client not configured. Simulating warm follow-up for %s", lead.lead_id)
            return {"status": "simulated", "body": body}

        message = self.client.messages.create(
            from_=self.settings.twilio_whatsapp_from,
            to=f"whatsapp:{lead.phone_number}",
            body=body,
        )
        return {"status": message.status, "sid": message.sid}
