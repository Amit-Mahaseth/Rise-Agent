"""
Twilio client for voice calling and WhatsApp messaging.
"""

from typing import Optional, Dict
import structlog
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.base.exceptions import TwilioException

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TwilioClient:
    """
    Client for Twilio voice and messaging services.
    """

    def __init__(self):
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.from_number = settings.twilio_voice_from
        self.whatsapp_from = settings.twilio_whatsapp_from
        self.client: Optional[Client] = None

    def _get_client(self) -> Client:
        """Get or create Twilio client."""
        if self.client is None:
            if not self.account_sid or not self.auth_token:
                raise ValueError("Twilio credentials not configured")
            self.client = Client(self.account_sid, self.auth_token)
        return self.client

    async def make_call(
        self,
        to_number: str,
        call_id: str,
        language: str = "en"
    ) -> tuple[bool, str | None]:
        """
        Initiate outbound voice call.

        Args:
            to_number: Phone number to call
            call_id: Unique call identifier
            language: Language for the call

        Returns:
            Tuple of (success, call_sid)
        """
        try:
            client = self._get_client()

            # Create TwiML for the call
            twiml = self._create_call_twiml(call_id, language)

            # Make the call
            call = client.calls.create(
                to=to_number,
                from_=self.from_number,
                twiml=twiml,
                status_callback=self._get_status_callback_url(),
                status_callback_events=['initiated', 'answered', 'completed', 'failed'],
                status_callback_method='POST'
            )

            logger.info(
                "Call initiated",
                call_sid=call.sid,
                to=to_number,
                call_id=call_id
            )

            return True, call.sid

        except TwilioException as e:
            logger.error(
                "Twilio call failed",
                error=str(e),
                to=to_number,
                call_id=call_id
            )
            return False, None
        except Exception as e:
            logger.error(
                "Unexpected error making call",
                error=str(e),
                to=to_number,
                call_id=call_id
            )
            return False, None

    def _create_call_twiml(self, call_id: str, language: str) -> str:
        """
        Create TwiML for voice call.

        Args:
            call_id: Call identifier
            language: Language code

        Returns:
            TwiML string
        """
        response = VoiceResponse()

        # Initial greeting
        greeting = self._get_greeting_text(language)
        response.say(greeting, voice='alice', language=self._get_twilio_language(language))

        # Gather speech input
        gather = Gather(
            input='speech',
            action=f'/api/v1/calls/{call_id}/process-speech',
            method='POST',
            timeout=5,
            speech_timeout='auto',
            language=language
        )
        gather.say("How can I help you today?", voice='alice', language=self._get_twilio_language(language))

        response.append(gather)

        # If no input, hang up
        response.say("Thank you for calling. Goodbye.", voice='alice', language=self._get_twilio_language(language))
        response.hangup()

        return str(response)

    async def send_whatsapp_message(
        self,
        to_number: str,
        message: str
    ) -> bool:
        """
        Send WhatsApp message.

        Args:
            to_number: WhatsApp number (format: whatsapp:+1234567890)
            message: Message content

        Returns:
            True if message sent successfully
        """
        try:
            client = self._get_client()

            message_obj = client.messages.create(
                body=message,
                from_=self.whatsapp_from,
                to=to_number
            )

            logger.info(
                "WhatsApp message sent",
                message_sid=message_obj.sid,
                to=to_number,
                message_length=len(message)
            )

            return True

        except TwilioException as e:
            logger.error(
                "WhatsApp message failed",
                error=str(e),
                to=to_number
            )
            return False
        except Exception as e:
            logger.error(
                "Unexpected error sending WhatsApp",
                error=str(e),
                to=to_number
            )
            return False

    async def handle_call_status_callback(
        self,
        call_sid: str,
        status: str,
        call_data: Dict = None
    ):
        """
        Handle call status callback from Twilio.

        Args:
            call_sid: Twilio call SID
            status: Call status
            call_data: Additional call data
        """
        logger.info(
            "Call status update",
            call_sid=call_sid,
            status=status,
            data=call_data
        )

        # This would trigger updates in the voice service
        # Implementation depends on webhook handling

    def _get_greeting_text(self, language: str) -> str:
        """
        Get greeting text for language.

        Args:
            language: Language code

        Returns:
            Greeting text
        """
        greetings = {
            "en": "Hello! Thank you for your interest in Rupeezy. This is RiseAgent.",
            "hi": "नमस्ते! रुपीज़ी में आपकी रुचि के लिए धन्यवाद। मैं RiseAgent हूं।",
            "mr": "नमस्कार! रुपीज़ीमध्ये तुमच्या 관심ाबद्दल धन्यवाद. मी RiseAgent आहे.",
            "ta": "வணக்கம்! ரூபீஸியில் உங்கள் ஆர்வத்திற்கு நன்றி. நான் RiseAgent.",
            "te": "నమస్కారం! రూపీజీలో మీ ఆసక్తికి ధన్యవాదాలు. నేను RiseAgent.",
            "gu": "નમસ્તે! રૂપીઝીમાં તમારી રુચિ બદલ આભાર. હું RiseAgent છું.",
            "bn": "নমস্কার! রূপীজিতে আপনার আগ্রহের জন্য ধন্যবাদ। আমি RiseAgent।",
        }

        return greetings.get(language, greetings["en"])

    def _get_twilio_language(self, language: str) -> str:
        """
        Get Twilio language code.

        Args:
            language: Our language code

        Returns:
            Twilio language code
        """
        twilio_langs = {
            "en": "en-US",
            "hi": "hi-IN",
            "mr": "mr-IN",
            "ta": "ta-IN",
            "te": "te-IN",
            "gu": "gu-IN",
            "bn": "bn-IN",
        }

        return twilio_langs.get(language, "en-US")

    def _get_status_callback_url(self) -> str:
        """
        Get status callback URL.

        Returns:
            Callback URL
        """
        base_url = settings.public_base_url
        return f"{base_url}/api/v1/webhooks/twilio/call-status"

    async def get_call_details(self, call_sid: str) -> Optional[Dict]:
        """
        Get call details from Twilio.

        Args:
            call_sid: Twilio call SID

        Returns:
            Call details or None
        """
        try:
            client = self._get_client()
            call = client.calls(call_sid).fetch()

            return {
                "sid": call.sid,
                "status": call.status,
                "duration": call.duration,
                "direction": call.direction,
                "from_number": call.from_,
                "to_number": call.to,
                "start_time": call.start_time,
                "end_time": call.end_time,
            }

        except Exception as e:
            logger.error("Failed to get call details", error=str(e), call_sid=call_sid)
            return None