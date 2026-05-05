"""
Lead service for RiseAgent AI.
Handles lead CRUD operations and business logic.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
import structlog

from app import models, schemas
from app.core.config import settings
from app.services.scoring_service import ScoringService
from app.services.whatsapp_service import WhatsAppService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LeadService:
    """
    Service class for lead management operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.scoring_service = ScoringService(db)
        self.whatsapp_service = WhatsAppService()

    async def create_lead(self, lead_in: schemas.LeadCreate) -> models.Lead:
        """
        Create a new lead.

        Args:
            lead_in: Lead creation data

        Returns:
            Created lead model instance
        """
        # Check if lead_id already exists
        existing = await self.db.execute(
            select(models.Lead).where(models.Lead.lead_id == lead_in.lead_id)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Lead with ID {lead_in.lead_id} already exists")

        # Create lead model
        lead = models.Lead(
            lead_id=lead_in.lead_id,
            full_name=lead_in.full_name,
            phone_number=lead_in.phone_number,
            email=lead_in.email,
            source=lead_in.source,
            product_interest=lead_in.product_interest,
            initial_context=lead_in.initial_context,
            notes=lead_in.notes,
            preferred_language=lead_in.preferred_language,
            communication_preference=lead_in.communication_preference,
        )

        self.db.add(lead)
        await self.db.commit()
        await self.db.refresh(lead)

        logger.info("Lead created", lead_id=lead.lead_id, name=lead.full_name)
        return lead

    async def get_lead(self, lead_id: str) -> Optional[models.Lead]:
        """
        Get lead by ID.

        Args:
            lead_id: Lead identifier

        Returns:
            Lead model instance or None
        """
        result = await self.db.execute(
            select(models.Lead).where(models.Lead.lead_id == lead_id)
        )
        return result.scalar_one_or_none()

    async def get_lead_with_stats(self, lead_id: str) -> Optional[schemas.LeadWithStats]:
        """
        Get lead with conversation and call statistics.

        Args:
            lead_id: Lead identifier

        Returns:
            Lead with stats schema or None
        """
        lead = await self.get_lead(lead_id)
        if not lead:
            return None

        # Get statistics
        stats = await self._get_lead_stats(lead_id)

        # Convert to schema
        lead_dict = {
            "id": lead.id,
            "lead_id": lead.lead_id,
            "full_name": lead.full_name,
            "phone_number": lead.phone_number,
            "email": lead.email,
            "source": lead.source,
            "product_interest": lead.product_interest,
            "initial_context": lead.initial_context,
            "notes": lead.notes,
            "status": lead.status,
            "preferred_language": lead.preferred_language,
            "communication_preference": lead.communication_preference,
            "assigned_rm": lead.assigned_rm,
            "classification": lead.classification,
            "score": lead.score,
            "rm_handoff_reason": lead.rm_handoff_reason,
            "whatsapp_sent": lead.whatsapp_sent,
            "whatsapp_link": lead.whatsapp_link,
            "created_at": lead.created_at,
            "updated_at": lead.updated_at,
            "last_contacted_at": lead.last_contacted_at,
            "qualified_at": lead.qualified_at,
            "converted_at": lead.converted_at,
            "metadata": lead.metadata,
            **stats
        }

        return schemas.LeadWithStats(**lead_dict)

    async def list_leads(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        classification: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[schemas.LeadSummary]:
        """
        List leads with optional filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status
            classification: Filter by classification
            source: Filter by source

        Returns:
            List of lead summaries
        """
        query = select(models.Lead)

        if status:
            query = query.where(models.Lead.status == status)
        if classification:
            query = query.where(models.Lead.classification == classification)
        if source:
            query = query.where(models.Lead.source == source)

        query = query.offset(skip).limit(limit).order_by(models.Lead.created_at.desc())

        result = await self.db.execute(query)
        leads = result.scalars().all()

        return [
            schemas.LeadSummary(
                id=lead.id,
                lead_id=lead.lead_id,
                full_name=lead.full_name,
                phone_number=lead.phone_number,
                status=lead.status,
                classification=lead.classification,
                score=lead.score,
                created_at=lead.created_at,
                last_contacted_at=lead.last_contacted_at,
            )
            for lead in leads
        ]

    async def update_lead(
        self,
        lead_id: str,
        lead_update: schemas.LeadUpdate
    ) -> Optional[models.Lead]:
        """
        Update lead information.

        Args:
            lead_id: Lead identifier
            lead_update: Update data

        Returns:
            Updated lead model instance or None
        """
        lead = await self.get_lead(lead_id)
        if not lead:
            return None

        # Update fields
        update_data = lead_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(lead, field, value)

        lead.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(lead)

        return lead

    async def delete_lead(self, lead_id: str) -> bool:
        """
        Soft delete a lead by marking as inactive.

        Args:
            lead_id: Lead identifier

        Returns:
            True if deleted, False if not found
        """
        lead = await self.get_lead(lead_id)
        if not lead:
            return False

        # Soft delete by updating status
        lead.status = "deleted"
        lead.updated_at = datetime.utcnow()
        await self.db.commit()

        return True

    async def qualify_lead(self, lead_id: str) -> Optional[schemas.LeadQualificationResult]:
        """
        Qualify lead based on conversation history and scoring.

        Args:
            lead_id: Lead identifier

        Returns:
            Qualification result or None
        """
        # Get latest scoring for the lead
        scoring = await self.scoring_service.get_latest_scoring(lead_id)
        if not scoring:
            return None

        # Determine classification and actions
        classification = scoring.classification or "cold"
        confidence_score = scoring.overall_score

        # Generate reasoning
        reasoning = self._generate_qualification_reasoning(scoring)

        # Determine recommended actions
        rm_handoff_required = classification == "hot"
        whatsapp_followup_required = classification == "warm"

        # Update lead
        await self.update_lead(
            lead_id,
            schemas.LeadUpdate(
                classification=classification,
                score=confidence_score,
                qualified_at=datetime.utcnow()
            )
        )

        return schemas.LeadQualificationResult(
            lead_id=lead_id,
            session_id=scoring.session_id,
            classification=classification,
            confidence_score=confidence_score,
            reasoning=reasoning,
            recommended_action=self._get_recommended_action(classification),
            rm_handoff_required=rm_handoff_required,
            whatsapp_followup_required=whatsapp_followup_required,
        )

    async def send_whatsapp_followup(self, lead_id: str) -> bool:
        """
        Send WhatsApp follow-up message to lead.

        Args:
            lead_id: Lead identifier

        Returns:
            True if sent successfully
        """
        lead = await self.get_lead(lead_id)
        if not lead or lead.classification != "warm" or lead.whatsapp_sent:
            return False

        # Send WhatsApp message
        success = await self.whatsapp_service.send_followup_message(
            lead.phone_number,
            lead.full_name,
            settings.WARM_FOLLOWUP_URL
        )

        if success:
            # Update lead
            await self.update_lead(
                lead_id,
                schemas.LeadUpdate(
                    whatsapp_sent=True,
                    whatsapp_link=settings.WARM_FOLLOWUP_URL
                )
            )

        return success

    async def handoff_to_rm(
        self,
        lead_id: str,
        rm_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Handoff lead to Relationship Manager.

        Args:
            lead_id: Lead identifier
            rm_id: RM identifier
            reason: Handoff reason

        Returns:
            True if handed off successfully
        """
        lead = await self.get_lead(lead_id)
        if not lead or lead.classification != "hot":
            return False

        # Update lead
        await self.update_lead(
            lead_id,
            schemas.LeadUpdate(
                assigned_rm=rm_id,
                rm_handoff_reason=reason,
                status="assigned"
            )
        )

        # TODO: Send notification to RM via webhook
        # await self._notify_rm_handoff(lead, rm_id, reason)

        return True

    async def _get_lead_stats(self, lead_id: str) -> dict:
        """
        Get lead statistics.

        Args:
            lead_id: Lead identifier

        Returns:
            Statistics dictionary
        """
        # Count calls
        calls_result = await self.db.execute(
            select(func.count(models.CallRecord.id))
            .where(models.CallRecord.lead_id == lead_id)
        )
        total_calls = calls_result.scalar()

        # Count conversations
        conv_result = await self.db.execute(
            select(func.count(models.Conversation.id))
            .where(models.Conversation.lead_id == lead_id)
        )
        total_conversations = conv_result.scalar()

        # Get last call duration
        last_call_result = await self.db.execute(
            select(models.CallRecord.duration_seconds)
            .where(models.CallRecord.lead_id == lead_id)
            .order_by(models.CallRecord.created_at.desc())
            .limit(1)
        )
        last_call_duration = last_call_result.scalar()

        # Get average score
        avg_score_result = await self.db.execute(
            select(func.avg(models.Scoring.overall_score))
            .where(models.Scoring.lead_id == lead_id)
        )
        average_score = avg_score_result.scalar()

        return {
            "total_calls": total_calls or 0,
            "total_conversations": total_conversations or 0,
            "last_call_duration": last_call_duration,
            "average_score": float(average_score) if average_score else None,
        }

    def _generate_qualification_reasoning(self, scoring: models.Scoring) -> str:
        """
        Generate human-readable reasoning for qualification.

        Args:
            scoring: Scoring model instance

        Returns:
            Reasoning string
        """
        reasons = []

        if scoring.intent_score > 0.7:
            reasons.append("Strong purchase intent detected")
        elif scoring.intent_score < 0.3:
            reasons.append("Low purchase intent")

        if scoring.engagement_score > 0.7:
            reasons.append("High engagement throughout conversation")
        elif scoring.engagement_score < 0.3:
            reasons.append("Low engagement levels")

        if scoring.objection_score > 0.7:
            reasons.append("All objections successfully handled")
        elif scoring.objection_count > 0:
            reasons.append(f"{scoring.objection_count} objections raised")

        if scoring.tone_score > 0.7:
            reasons.append("Positive tone maintained")
        elif scoring.tone_score < 0.3:
            reasons.append("Negative or disinterested tone")

        return ". ".join(reasons)

    def _get_recommended_action(self, classification: str) -> str:
        """
        Get recommended action based on classification.

        Args:
            classification: Lead classification

        Returns:
            Recommended action string
        """
        actions = {
            "hot": "Immediate handoff to Relationship Manager with full context",
            "warm": "Send WhatsApp follow-up with application link",
            "cold": "Add to nurture campaign for future re-engagement"
        }
        return actions.get(classification, "Review manually")