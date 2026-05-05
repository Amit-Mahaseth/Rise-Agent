"""
Conversation service for RiseAgent AI.
Handles conversation orchestration using LangChain and LLM.
"""

from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app import models, schemas
from app.core.llm.langchain_setup import (
    get_conversation_chain,
    CONVERSATION_PROMPT,
    OBJECTION_HANDLING_PROMPT,
    QUALIFICATION_PROMPT
)
from app.core.memory.memory_manager import MemoryManager
from app.core.rag.retriever import RAGRetriever
from app.services.scoring_service import ScoringService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ConversationService:
    """
    Service for managing AI conversations with leads.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.memory_manager = MemoryManager(db)
        self.rag_retriever = RAGRetriever()
        self.scoring_service = ScoringService(db)

    async def process_user_input(
        self,
        lead_id: str,
        session_id: str,
        user_input: str,
        language: str = "en"
    ) -> Tuple[str, Dict]:
        """
        Process user input and generate AI response.

        Args:
            lead_id: Lead identifier
            session_id: Conversation session ID
            user_input: User's message/input
            language: Detected language

        Returns:
            Tuple of (response_text, metadata_dict)
        """
        try:
            # Retrieve conversation context
            context = await self.memory_manager.get_context(lead_id, session_id)

            # Retrieve relevant knowledge
            script_content = await self.rag_retriever.get_script_content()
            faq_content = await self.rag_retriever.get_faq_content(user_input)

            # Get conversation chain
            chain = get_conversation_chain()

            # Generate response
            response = await chain.apredict(
                input=user_input,
                context=context,
                script=script_content,
                faq=faq_content
            )

            # Analyze response for metadata
            metadata = await self._analyze_response(user_input, response, language)

            # Store conversation
            await self._store_conversation(
                lead_id, session_id, "user", user_input, language, metadata
            )
            await self._store_conversation(
                lead_id, session_id, "assistant", response, language, metadata
            )

            # Update memory
            await self.memory_manager.update_memory(lead_id, session_id, user_input, response)

            # Update scoring
            await self.scoring_service.update_scoring(lead_id, session_id, metadata)

            logger.info(
                "Conversation processed",
                lead_id=lead_id,
                session_id=session_id,
                input_length=len(user_input),
                response_length=len(response)
            )

            return response, metadata

        except Exception as e:
            logger.error(
                "Failed to process conversation",
                error=str(e),
                lead_id=lead_id,
                session_id=session_id
            )
            # Return fallback response
            fallback_response = "I apologize, but I'm having trouble processing your request. Could you please try again?"
            return fallback_response, {"error": str(e)}

    async def handle_objection(
        self,
        lead_id: str,
        session_id: str,
        objection: str,
        context: str
    ) -> str:
        """
        Handle customer objection with specialized response.

        Args:
            lead_id: Lead identifier
            session_id: Session identifier
            objection: The objection raised
            context: Conversation context

        Returns:
            Objection handling response
        """
        try:
            # Get relevant FAQ content
            faq_content = await self.rag_retriever.get_faq_content(objection)

            # Use objection handling prompt
            chain = get_conversation_chain()

            response = await chain.apredict(
                objection=objection,
                context=context,
                faq=faq_content
            )

            # Store objection handling
            metadata = {
                "objection_type": objection,
                "objection_handled": True,
                "faq_used": bool(faq_content)
            }

            await self._store_conversation(
                lead_id, session_id, "assistant",
                response, "en", metadata
            )

            logger.info(
                "Objection handled",
                lead_id=lead_id,
                session_id=session_id,
                objection=objection[:100]
            )

            return response

        except Exception as e:
            logger.error("Failed to handle objection", error=str(e))
            return "I understand your concern. Let me connect you with a human representative who can better assist you."

    async def qualify_conversation(
        self,
        lead_id: str,
        session_id: str
    ) -> Dict:
        """
        Qualify the conversation and provide scoring.

        Args:
            lead_id: Lead identifier
            session_id: Session identifier

        Returns:
            Qualification results
        """
        try:
            # Get conversation history
            history = await self.memory_manager.get_full_history(lead_id, session_id)

            # Use qualification prompt
            chain = get_conversation_chain()

            scoring_criteria = """
            Intent: Signs of interest in financial products, asking about rates, eligibility, etc.
            Engagement: Active participation, asking questions, providing information.
            Objections: Concerns raised and how they were addressed.
            Tone: Overall positivity and willingness to continue conversation.
            """

            result = await chain.apredict(
                conversation_history=history,
                scoring_criteria=scoring_criteria
            )

            # Parse and store scoring
            scores = self._parse_scoring_result(result)
            await self.scoring_service.create_scoring(lead_id, session_id, scores)

            logger.info(
                "Conversation qualified",
                lead_id=lead_id,
                session_id=session_id,
                classification=scores.get("classification")
            )

            return scores

        except Exception as e:
            logger.error("Failed to qualify conversation", error=str(e))
            return {"classification": "unknown", "error": str(e)}

    async def _store_conversation(
        self,
        lead_id: str,
        session_id: str,
        message_type: str,
        content: str,
        language: str,
        metadata: Dict
    ):
        """
        Store conversation message in database.

        Args:
            lead_id: Lead identifier
            session_id: Session identifier
            message_type: Type of message
            content: Message content
            language: Language code
            metadata: Additional metadata
        """
        conversation = models.Conversation(
            lead_id=lead_id,
            session_id=session_id,
            message_type=message_type,
            content=content,
            language=language,
            intent=metadata.get("intent"),
            intent_confidence=metadata.get("intent_confidence"),
            sentiment=metadata.get("sentiment"),
            sentiment_score=metadata.get("sentiment_score"),
            objection_type=metadata.get("objection_type"),
            objection_handled=metadata.get("objection_handled"),
            response_time_ms=metadata.get("response_time_ms"),
            tokens_used=metadata.get("tokens_used")
        )

        self.db.add(conversation)
        await self.db.commit()

    async def _analyze_response(
        self,
        user_input: str,
        response: str,
        language: str
    ) -> Dict:
        """
        Analyze the conversation turn for metadata.

        Args:
            user_input: User's input
            response: AI response
            language: Language code

        Returns:
            Metadata dictionary
        """
        # Simple analysis - in production, this would use more sophisticated NLP
        metadata = {
            "input_length": len(user_input),
            "response_length": len(response),
            "language": language,
            "has_question": "?" in user_input,
            "has_objection": any(word in user_input.lower() for word in
                               ["can't", "don't", "won't", "not sure", "expensive", "risk"]),
            "sentiment": "neutral",  # Would use sentiment analysis
            "intent": "general",  # Would use intent classification
        }

        # Estimate response time (mock)
        metadata["response_time_ms"] = 500 + len(response) * 10
        metadata["tokens_used"] = (len(user_input) + len(response)) // 4

        return metadata

    def _parse_scoring_result(self, result: str) -> Dict:
        """
        Parse the qualification result string into structured data.

        Args:
            result: Raw qualification result

        Returns:
            Parsed scoring dictionary
        """
        # Simple parsing - in production, use structured output
        scores = {
            "intent_score": 0.5,
            "engagement_score": 0.5,
            "objection_score": 0.5,
            "tone_score": 0.5,
            "overall_score": 0.5,
            "classification": "warm"
        }

        # Look for classification keywords
        result_lower = result.lower()
        if "hot" in result_lower:
            scores["classification"] = "hot"
            scores["overall_score"] = 0.8
        elif "cold" in result_lower:
            scores["classification"] = "cold"
            scores["overall_score"] = 0.3

        return scores