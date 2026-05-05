"""
LangChain setup and configuration for RiseAgent AI.
"""

from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseLanguageModel
import structlog

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Global variables for LangChain components
_llm_instance = None
_conversation_chain = None


async def initialize_langchain():
    """
    Initialize LangChain components.
    """
    global _llm_instance, _conversation_chain

    try:
        # Initialize LLM
        _llm_instance = await _create_llm_instance()

        # Initialize conversation chain
        _conversation_chain = _create_conversation_chain(_llm_instance)

        logger.info("LangChain initialized successfully")

    except Exception as e:
        logger.error("Failed to initialize LangChain", error=str(e))
        raise


async def _create_llm_instance() -> BaseLanguageModel:
    """
    Create LLM instance based on configuration.

    Returns:
        Configured LLM instance
    """
    if settings.llm_provider.lower() == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=settings.llm_model,
            anthropic_api_key=settings.anthropic_api_key,
            temperature=0.7,
            max_tokens=1000,
        )

    elif settings.llm_provider.lower() == "mistral":
        from langchain_mistralai import ChatMistralAI

        return ChatMistralAI(
            model=settings.llm_model,
            mistral_api_key=settings.mistral_api_key,
            temperature=0.7,
            max_tokens=1000,
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")


def _create_conversation_chain(llm: BaseLanguageModel) -> ConversationChain:
    """
    Create conversation chain with memory.

    Args:
        llm: Language model instance

    Returns:
        Configured conversation chain
    """
    # Memory for conversation context
    memory = ConversationBufferWindowMemory(
        k=10,  # Keep last 10 exchanges
        memory_key="chat_history",
        return_messages=True
    )

    # Create conversation chain
    chain = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=settings.DEBUG
    )

    return chain


def get_conversation_chain() -> ConversationChain:
    """
    Get the global conversation chain instance.

    Returns:
        Conversation chain instance
    """
    if _conversation_chain is None:
        raise RuntimeError("LangChain not initialized. Call initialize_langchain() first.")
    return _conversation_chain


def get_llm_instance() -> BaseLanguageModel:
    """
    Get the global LLM instance.

    Returns:
        LLM instance
    """
    if _llm_instance is None:
        raise RuntimeError("LangChain not initialized. Call initialize_langchain() first.")
    return _llm_instance


# Prompt templates for different conversation scenarios
CONVERSATION_PROMPT = PromptTemplate(
    input_variables=["chat_history", "input", "context", "script", "faq"],
    template="""
You are RiseAgent, an AI voice assistant for Rupeezy fintech company. Your goal is to qualify leads for financial products through natural conversation.

CONTEXT:
{context}

CONVERSATION SCRIPT:
{script}

FAQ KNOWLEDGE:
{faq}

CHAT HISTORY:
{chat_history}

CURRENT USER INPUT: {input}

Respond naturally as if you're speaking on a phone call. Keep responses conversational, not robotic. Handle objections using the FAQ knowledge. Focus on qualifying the lead's intent, engagement, and readiness for financial products.

If the user shows strong interest, guide them towards next steps. If they have objections, address them calmly. Always maintain a professional, helpful tone.
"""
)

OBJECTION_HANDLING_PROMPT = PromptTemplate(
    input_variables=["objection", "context", "faq"],
    template="""
Analyze this customer objection and provide a natural response:

OBJECTION: {objection}

CONTEXT: {context}

FAQ KNOWLEDGE: {faq}

Provide a conversational response that addresses the objection while maintaining rapport. Focus on understanding their concern and providing relevant information from the FAQ.
"""
)

QUALIFICATION_PROMPT = PromptTemplate(
    input_variables=["conversation_history", "scoring_criteria"],
    template="""
Analyze this conversation and provide qualification scoring:

CONVERSATION:
{conversation_history}

SCORING CRITERIA:
{scoring_criteria}

Provide scores for:
- Intent (0-1): How interested are they in financial products?
- Engagement (0-1): How engaged are they in the conversation?
- Objections (0-1): How well were objections handled?
- Tone (0-1): How positive is their overall tone?

Also provide overall classification: Hot/Warm/Cold
"""
)