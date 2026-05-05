"""
Conversation engine — LangChain + Claude with RAG retrieval.
Manages the full conversation flow for each call.
"""

from __future__ import annotations

import logging
from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from config import get_settings
from knowledge.loader import get_retriever
from prompts.system_prompt import build_system_prompt

logger = logging.getLogger("riseagent.conversation")


class ConversationSession:
    """
    Manages a single call's conversation with Claude + RAG.
    Each call gets its own session with in-call turn memory.
    """

    def __init__(
        self,
        lead_id: str,
        lead_name: str,
        language: str = "Hindi",
        lead_memory: str = "No previous interactions.",
    ):
        self.lead_id = lead_id
        self.lead_name = lead_name
        self.language = language
        self.lead_memory = lead_memory
        self.turn_count = 0
        self.transcript: list[dict] = []

        settings = get_settings()

        # Initialize Claude LLM
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            anthropic_api_key=settings.anthropic_api_key,
            max_tokens=300,
            temperature=0.7,
        )

        # Build system prompt
        self.system_prompt = build_system_prompt(
            detected_language=language,
            lead_memory=lead_memory,
        )

        # In-call conversation memory (turn-by-turn)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
        )

        # RAG retriever for AP knowledge base
        self.retriever = get_retriever(k=3)

        # Conversational retrieval chain
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            memory=self.memory,
            return_source_documents=False,
            verbose=False,
        )

        logger.info(
            "Conversation session created for lead %s [%s]",
            lead_id, language,
        )

    async def get_opening(self) -> str:
        """Generate the opening greeting for the call."""
        self.turn_count += 1
        opening_prompt = (
            f"You are starting a new sales call with {self.lead_name}. "
            f"Give a warm, natural opening in {self.language}. "
            f"Introduce yourself as calling from Rupeezy about the AP program. "
            f"Ask if they have 2 minutes."
        )

        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=opening_prompt),
            ]
            response = await self.llm.ainvoke(messages)
            agent_text = response.content.strip()

            self.transcript.append({
                "turn": self.turn_count,
                "speaker": "agent",
                "text": agent_text,
            })

            logger.info("Opening [turn %d]: %s", self.turn_count, agent_text[:80])
            return agent_text
        except Exception as exc:
            logger.error("Failed to generate opening: %s", exc)
            fallback = f"Hi {self.lead_name}, this is a quick call from Rupeezy. Do you have 2 minutes?"
            self.transcript.append({"turn": self.turn_count, "speaker": "agent", "text": fallback})
            return fallback

    async def process_turn(self, lead_text: str) -> str:
        """
        Process a single conversation turn.
        Takes the lead's text input, runs it through the chain, returns agent response.
        """
        self.turn_count += 1

        # Log lead's message
        self.transcript.append({
            "turn": self.turn_count,
            "speaker": "lead",
            "text": lead_text,
        })

        try:
            # Build the query with context
            query = (
                f"[System context: Language={self.language}, Turn={self.turn_count}, "
                f"Lead name={self.lead_name}]\n"
                f"Lead says: \"{lead_text}\"\n"
                f"Respond as the sales agent in {self.language}."
            )

            result = await self.chain.ainvoke({"question": query})
            agent_text = result.get("answer", "").strip()

            if not agent_text:
                agent_text = "I understand. Let me tell you more about the program."

            self.turn_count += 1
            self.transcript.append({
                "turn": self.turn_count,
                "speaker": "agent",
                "text": agent_text,
            })

            logger.info("Turn %d agent: %s", self.turn_count, agent_text[:80])
            return agent_text
        except Exception as exc:
            logger.error("Conversation turn error: %s", exc)
            fallback = "I appreciate your time. Let me share one more thing about the program."
            self.turn_count += 1
            self.transcript.append({"turn": self.turn_count, "speaker": "agent", "text": fallback})
            return fallback

    def update_language(self, new_language: str) -> None:
        """Update the conversation language mid-call."""
        self.language = new_language
        self.system_prompt = build_system_prompt(
            detected_language=new_language,
            lead_memory=self.lead_memory,
        )
        logger.info("Language updated to %s for lead %s", new_language, self.lead_id)

    def get_full_transcript(self) -> str:
        """Return the full transcript as a formatted string."""
        lines = []
        for entry in self.transcript:
            speaker = "Agent" if entry["speaker"] == "agent" else "Lead"
            lines.append(f"{speaker}: {entry['text']}")
        return "\n".join(lines)

    def get_transcript_entries(self) -> list[dict]:
        """Return raw transcript entries."""
        return self.transcript


async def generate_call_summary(transcript: str) -> str:
    """Generate a 2-sentence summary of a completed call using Claude."""
    from prompts.system_prompt import build_summary_prompt

    settings = get_settings()
    try:
        llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            anthropic_api_key=settings.anthropic_api_key,
            max_tokens=150,
            temperature=0.3,
        )
        prompt = build_summary_prompt(transcript)
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as exc:
        logger.error("Summary generation failed: %s", exc)
        return "Call completed. Summary unavailable."
