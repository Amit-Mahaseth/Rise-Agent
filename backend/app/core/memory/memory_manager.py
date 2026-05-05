"""
Memory manager for conversation context using ChromaDB.
"""

from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.memory.chromadb_client import ChromaDBClient
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryManager:
    """
    Manages conversation memory and context retrieval.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.chroma_client = ChromaDBClient()

    async def get_context(self, lead_id: str, session_id: str) -> str:
        """
        Retrieve conversation context for a lead.

        Args:
            lead_id: Lead identifier
            session_id: Session identifier

        Returns:
            Formatted context string
        """
        try:
            # Get recent conversation history
            history = await self._get_recent_history(lead_id, session_id, limit=5)

            # Get relevant memories from vector store
            memories = await self.chroma_client.search_memories(
                query=f"lead_{lead_id}_context",
                n_results=3
            )

            # Combine history and memories
            context_parts = []

            if history:
                context_parts.append("Recent conversation:")
                context_parts.extend([f"- {msg['role']}: {msg['content']}" for msg in history])

            if memories:
                context_parts.append("\nRelevant past context:")
                context_parts.extend([f"- {mem['content']}" for mem in memories])

            return "\n".join(context_parts) if context_parts else "New conversation"

        except Exception as e:
            logger.error("Failed to get context", error=str(e), lead_id=lead_id)
            return "New conversation"

    async def update_memory(
        self,
        lead_id: str,
        session_id: str,
        user_input: str,
        ai_response: str
    ):
        """
        Update conversation memory with new exchange.

        Args:
            lead_id: Lead identifier
            session_id: Session identifier
            user_input: User's message
            ai_response: AI response
        """
        try:
            # Create memory entry
            memory_text = f"User: {user_input}\nAssistant: {ai_response}"

            # Store in vector database
            await self.chroma_client.store_memory(
                text=memory_text,
                metadata={
                    "lead_id": lead_id,
                    "session_id": session_id,
                    "type": "conversation_exchange"
                },
                id=f"{lead_id}_{session_id}_{len(memory_text)}"
            )

            logger.debug(
                "Memory updated",
                lead_id=lead_id,
                session_id=session_id,
                memory_length=len(memory_text)
            )

        except Exception as e:
            logger.error("Failed to update memory", error=str(e), lead_id=lead_id)

    async def get_full_history(self, lead_id: str, session_id: str) -> str:
        """
        Get complete conversation history for qualification.

        Args:
            lead_id: Lead identifier
            session_id: Session identifier

        Returns:
            Formatted conversation history
        """
        try:
            history = await self._get_recent_history(lead_id, session_id, limit=50)

            if not history:
                return "No conversation history available."

            formatted_history = []
            for msg in history:
                formatted_history.append(f"{msg['role'].title()}: {msg['content']}")

            return "\n".join(formatted_history)

        except Exception as e:
            logger.error("Failed to get full history", error=str(e))
            return "Error retrieving conversation history."

    async def _get_recent_history(
        self,
        lead_id: str,
        session_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent conversation history from database.

        Args:
            lead_id: Lead identifier
            session_id: Session identifier
            limit: Maximum messages to retrieve

        Returns:
            List of message dictionaries
        """
        from sqlalchemy import select
        from app import models

        result = await self.db.execute(
            select(models.Conversation)
            .where(
                models.Conversation.lead_id == lead_id,
                models.Conversation.session_id == session_id
            )
            .order_by(models.Conversation.timestamp.desc())
            .limit(limit)
        )

        conversations = result.scalars().all()

        # Convert to list and reverse to chronological order
        messages = []
        for conv in reversed(conversations):
            messages.append({
                "role": conv.message_type,
                "content": conv.content,
                "timestamp": conv.timestamp.isoformat(),
                "language": conv.language
            })

        return messages

    async def search_similar_conversations(
        self,
        lead_id: str,
        query: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Search for similar past conversations.

        Args:
            lead_id: Lead identifier
            query: Search query
            limit: Maximum results

        Returns:
            List of similar conversation snippets
        """
        try:
            # Search vector store for similar content
            results = await self.chroma_client.search_memories(
                query=f"lead_{lead_id} {query}",
                n_results=limit
            )

            return [
                {
                    "content": result["content"],
                    "similarity": result["similarity"],
                    "metadata": result["metadata"]
                }
                for result in results
            ]

        except Exception as e:
            logger.error("Failed to search similar conversations", error=str(e))
            return []