"""
WhatsApp service for messaging integration.
"""

from typing import Optional
import structlog

from app.core.telephony.twilio_client import TwilioClient
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WhatsAppService:
    """
    Service for WhatsApp messaging via Twilio.
    """

    def __init__(self):
        self.twilio_client = TwilioClient()

    async def send_followup_message(
        self,
        phone_number: str,
        customer_name: str,
        application_link: str
    ) -> bool:
        """
        Send WhatsApp follow-up message to warm lead.

        Args:
            phone_number: Customer phone number
            customer_name: Customer name
            application_link: Link to application

        Returns:
            True if message sent successfully
        """
        try:
            message_body = f"""
Hello {customer_name}!

Thank you for your interest in Rupeezy's financial products. Based on our conversation, here are some options that might suit your needs:

🔗 Apply now: {application_link}

Our team is here to help you every step of the way. Feel free to reach out if you have any questions!

Best regards,
RiseAgent
Rupeezy
            """.strip()

            # Format phone number for WhatsApp
            whatsapp_number = f"whatsapp:{phone_number}"

            success = await self.twilio_client.send_whatsapp_message(
                to_number=whatsapp_number,
                message=message_body
            )

            if success:
                logger.info(
                    "WhatsApp follow-up sent",
                    phone=phone_number,
                    name=customer_name
                )
            else:
                logger.error(
                    "Failed to send WhatsApp follow-up",
                    phone=phone_number,
                    name=customer_name
                )

            return success

        except Exception as e:
            logger.error(
                "Error sending WhatsApp follow-up",
                error=str(e),
                phone=phone_number
            )
            return False

    async def send_reminder_message(
        self,
        phone_number: str,
        customer_name: str,
        days_since_contact: int
    ) -> bool:
        """
        Send reminder message to cold leads.

        Args:
            phone_number: Customer phone number
            customer_name: Customer name
            days_since_contact: Days since last contact

        Returns:
            True if message sent successfully
        """
        try:
            message_body = f"""
Hi {customer_name},

We noticed it's been {days_since_contact} days since we last spoke. We're still here to help you with your financial needs!

Have you had a chance to consider Rupeezy's loan options? We're offering competitive rates and quick approval.

🔗 Check our current offers: https://rupeezy.com/offers

Reply to this message or call us if you'd like to discuss your options.

Best,
RiseAgent
Rupeezy
            """.strip()

            whatsapp_number = f"whatsapp:{phone_number}"

            success = await self.twilio_client.send_whatsapp_message(
                to_number=whatsapp_number,
                message=message_body
            )

            if success:
                logger.info(
                    "WhatsApp reminder sent",
                    phone=phone_number,
                    name=customer_name,
                    days_since=days_since_contact
                )

            return success

        except Exception as e:
            logger.error(
                "Error sending WhatsApp reminder",
                error=str(e),
                phone=phone_number
            )
            return False

    async def send_confirmation_message(
        self,
        phone_number: str,
        customer_name: str,
        application_id: str
    ) -> bool:
        """
        Send application confirmation message.

        Args:
            phone_number: Customer phone number
            customer_name: Customer name
            application_id: Application identifier

        Returns:
            True if message sent successfully
        """
        try:
            message_body = f"""
Hello {customer_name}!

Great news! Your application ({application_id}) has been received and is being processed.

📋 Application Status: Under Review
⏱️ Expected processing time: 24-48 hours

We'll keep you updated on the progress. If you have any questions, feel free to reply to this message.

Thank you for choosing Rupeezy!

Best regards,
RiseAgent
Rupeezy
            """.strip()

            whatsapp_number = f"whatsapp:{phone_number}"

            success = await self.twilio_client.send_whatsapp_message(
                to_number=whatsapp_number,
                message=message_body
            )

            if success:
                logger.info(
                    "WhatsApp confirmation sent",
                    phone=phone_number,
                    name=customer_name,
                    application_id=application_id
                )

            return success

        except Exception as e:
            logger.error(
                "Error sending WhatsApp confirmation",
                error=str(e),
                phone=phone_number
            )
            return False

    async def handle_incoming_message(
        self,
        from_number: str,
        message_body: str
    ) -> Optional[str]:
        """
        Handle incoming WhatsApp messages.

        Args:
            from_number: Sender's phone number
            message_body: Message content

        Returns:
            Response message or None
        """
        try:
            # Clean phone number
            clean_number = from_number.replace("whatsapp:", "")

            # Basic auto-responses based on message content
            message_lower = message_body.lower()

            if any(word in message_lower for word in ["status", "update", "progress"]):
                response = """
Your application is being processed. We'll send you an update within 24 hours.

For urgent inquiries, you can call our helpline: +91-XXXX-XXXXXX

Best,
RiseAgent
                """.strip()

            elif any(word in message_lower for word in ["help", "support", "question"]):
                response = """
I'm here to help! You can:

📞 Call us: +91-XXXX-XXXXXX
💬 Chat with our AI assistant
🌐 Visit: https://rupeezy.com

What specific question can I help you with?

Best,
RiseAgent
                """.strip()

            else:
                response = """
Thank you for your message. Our team will get back to you shortly.

For immediate assistance, call: +91-XXXX-XXXXXX

Best regards,
RiseAgent
Rupeezy
                """.strip()

            # Send response
            whatsapp_number = f"whatsapp:{clean_number}"
            await self.twilio_client.send_whatsapp_message(
                to_number=whatsapp_number,
                message=response
            )

            logger.info(
                "WhatsApp response sent",
                to=from_number,
                message_length=len(response)
            )

            return response

        except Exception as e:
            logger.error(
                "Error handling WhatsApp message",
                error=str(e),
                from_number=from_number
            )
            return None