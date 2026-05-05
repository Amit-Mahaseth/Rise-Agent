"""
Scoring service for lead qualification.
"""

from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app import models, schemas
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ScoringService:
    """
    Service for calculating and managing lead scores.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_scoring(
        self,
        lead_id: str,
        session_id: str,
        scores: Dict
    ) -> models.Scoring:
        """
        Create a new scoring record.

        Args:
            lead_id: Lead identifier
            session_id: Session identifier
            scores: Scoring data dictionary

        Returns:
            Created scoring model instance
        """
        # Calculate overall score
        overall_score = self._calculate_overall_score(scores)

        # Determine classification
        classification = self._determine_classification(overall_score)

        scoring = models.Scoring(
            lead_id=lead_id,
            session_id=session_id,
            intent_score=scores.get("intent_score", 0.0),
            engagement_score=scores.get("engagement_score", 0.0),
            objection_score=scores.get("objection_score", 0.0),
            tone_score=scores.get("tone_score", 0.0),
            overall_score=overall_score,
            classification=classification,
            conversation_length_seconds=scores.get("conversation_length", 0),
            message_count=scores.get("message_count", 0),
            user_message_count=scores.get("user_message_count", 0),
            assistant_message_count=scores.get("assistant_message_count", 0),
            objection_count=scores.get("objection_count", 0),
            objections_handled=scores.get("objections_handled", 0),
            positive_signals=scores.get("positive_signals", 0),
            positive_keywords=scores.get("positive_keywords"),
            language_consistency_score=scores.get("language_consistency", 1.0),
            communication_clarity_score=scores.get("communication_clarity", 1.0),
            scoring_metadata=scores.get("metadata")
        )

        self.db.add(scoring)
        await self.db.commit()
        await self.db.refresh(scoring)

        logger.info(
            "Scoring created",
            lead_id=lead_id,
            session_id=session_id,
            overall_score=overall_score,
            classification=classification
        )

        return scoring

    async def update_scoring(
        self,
        lead_id: str,
        session_id: str,
        metadata: Dict
    ):
        """
        Update scoring based on conversation metadata.

        Args:
            lead_id: Lead identifier
            session_id: Session identifier
            metadata: Conversation metadata
        """
        try:
            # Get or create scoring record
            scoring = await self.get_scoring(lead_id, session_id)
            if not scoring:
                # Create initial scoring
                scores = self._extract_scores_from_metadata(metadata)
                await self.create_scoring(lead_id, session_id, scores)
                return

            # Update existing scoring
            updates = self._extract_updates_from_metadata(metadata)

            for key, value in updates.items():
                if hasattr(scoring, key):
                    setattr(scoring, key, value)

            # Recalculate overall score
            scoring.overall_score = self._calculate_overall_score({
                "intent_score": scoring.intent_score,
                "engagement_score": scoring.engagement_score,
                "objection_score": scoring.objection_score,
                "tone_score": scoring.tone_score,
            })

            # Update classification
            scoring.classification = self._determine_classification(scoring.overall_score)

            await self.db.commit()

            logger.debug(
                "Scoring updated",
                lead_id=lead_id,
                session_id=session_id,
                overall_score=scoring.overall_score
            )

        except Exception as e:
            logger.error("Failed to update scoring", error=str(e), lead_id=lead_id)

    async def get_scoring(self, lead_id: str, session_id: str) -> Optional[models.Scoring]:
        """
        Get scoring record for a lead session.

        Args:
            lead_id: Lead identifier
            session_id: Session identifier

        Returns:
            Scoring model instance or None
        """
        result = await self.db.execute(
            select(models.Scoring)
            .where(
                models.Scoring.lead_id == lead_id,
                models.Scoring.session_id == session_id
            )
        )
        return result.scalar_one_or_none()

    async def get_latest_scoring(self, lead_id: str) -> Optional[models.Scoring]:
        """
        Get the latest scoring record for a lead.

        Args:
            lead_id: Lead identifier

        Returns:
            Latest scoring model instance or None
        """
        result = await self.db.execute(
            select(models.Scoring)
            .where(models.Scoring.lead_id == lead_id)
            .order_by(models.Scoring.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_scoring_history(self, lead_id: str, limit: int = 10) -> list[models.Scoring]:
        """
        Get scoring history for a lead.

        Args:
            lead_id: Lead identifier
            limit: Maximum records to return

        Returns:
            List of scoring records
        """
        result = await self.db.execute(
            select(models.Scoring)
            .where(models.Scoring.lead_id == lead_id)
            .order_by(models.Scoring.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    def _calculate_overall_score(self, scores: Dict) -> float:
        """
        Calculate overall score from component scores.

        Args:
            scores: Dictionary of component scores

        Returns:
            Overall score (0-1)
        """
        weights = {
            'intent': 0.4,
            'engagement': 0.3,
            'objection': 0.2,
            'tone': 0.1
        }

        overall = (
            scores.get("intent_score", 0) * weights['intent'] +
            scores.get("engagement_score", 0) * weights['engagement'] +
            scores.get("objection_score", 0) * weights['objection'] +
            scores.get("tone_score", 0) * weights['tone']
        )

        return round(overall, 3)

    def _determine_classification(self, overall_score: float) -> str:
        """
        Determine lead classification based on overall score.

        Args:
            overall_score: Overall score (0-1)

        Returns:
            Classification string
        """
        if overall_score >= settings.HOT_LEAD_THRESHOLD:
            return "hot"
        elif overall_score >= settings.WARM_LEAD_THRESHOLD:
            return "warm"
        else:
            return "cold"

    def _extract_scores_from_metadata(self, metadata: Dict) -> Dict:
        """
        Extract initial scores from conversation metadata.

        Args:
            metadata: Conversation metadata

        Returns:
            Initial scoring dictionary
        """
        return {
            "intent_score": 0.5,  # Default neutral
            "engagement_score": 1.0 if metadata.get("has_question") else 0.5,
            "objection_score": 0.3 if metadata.get("has_objection") else 0.8,
            "tone_score": 0.7,  # Default positive
            "conversation_length": 0,
            "message_count": 1,
            "user_message_count": 1,
            "assistant_message_count": 0,
            "objection_count": 1 if metadata.get("has_objection") else 0,
            "objections_handled": 0,
            "positive_signals": 1 if not metadata.get("has_objection") else 0,
            "language_consistency": 1.0,
            "communication_clarity": 0.8,
            "metadata": metadata
        }

    def _extract_updates_from_metadata(self, metadata: Dict) -> Dict:
        """
        Extract scoring updates from conversation metadata.

        Args:
            metadata: Conversation metadata

        Returns:
            Update dictionary
        """
        updates = {}

        # Update engagement based on questions
        if metadata.get("has_question"):
            updates["engagement_score"] = min(1.0, updates.get("engagement_score", 0.5) + 0.1)

        # Update objection score
        if metadata.get("has_objection"):
            updates["objection_count"] = updates.get("objection_count", 0) + 1
            updates["objection_score"] = max(0.0, updates.get("objection_score", 0.5) - 0.1)

        # Update message counts
        updates["message_count"] = updates.get("message_count", 0) + 1
        if metadata.get("message_type") == "user":
            updates["user_message_count"] = updates.get("user_message_count", 0) + 1
        else:
            updates["assistant_message_count"] = updates.get("assistant_message_count", 0) + 1

        return updates