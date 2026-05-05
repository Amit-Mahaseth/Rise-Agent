import logging

from app.core.config import Settings
from app.services.telephony.base import BaseCallProvider, CallProviderResponse

logger = logging.getLogger(__name__)


class TwilioCallProvider(BaseCallProvider):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = None
        if settings.twilio_account_sid and settings.twilio_auth_token:
            try:
                from twilio.rest import Client

                self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
            except ModuleNotFoundError:
                logger.warning("Twilio SDK not installed. Voice provider will stay in simulation mode.")

    def initiate_outbound_call(self, *, lead_id: str, call_id: str, phone_number: str) -> CallProviderResponse:
        if not self.client or not self.settings.twilio_voice_from:
            logger.warning("Twilio voice is not configured. Call %s will remain in simulation mode.", call_id)
            return CallProviderResponse(
                provider_call_id=None,
                status="simulation_pending",
                details={"reason": "missing_twilio_voice_configuration"},
            )

        voice_url = (
            f"{self.settings.public_base_url}{self.settings.api_prefix}/webhook/voice"
            f"?lead_id={lead_id}&call_id={call_id}"
        )
        status_callback = f"{self.settings.public_base_url}{self.settings.api_prefix}/calls/twilio/status"

        twilio_call = self.client.calls.create(
            to=phone_number,
            from_=self.settings.twilio_voice_from,
            url=voice_url,
            status_callback=status_callback,
            status_callback_event=["initiated", "ringing", "answered", "completed"],
        )
        return CallProviderResponse(
            provider_call_id=twilio_call.sid,
            status=twilio_call.status,
            details={"sid": twilio_call.sid},
        )
