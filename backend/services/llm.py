"""
LLM Router — Groq Primary, Gemini Fallback.
Lazy initialization to prevent crashes when env vars aren't loaded yet.
"""

import os
import logging
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

# ── Lazy singletons ────────────────────────────────────────────────
_groq_llm = None
_gemini_llm = None


def _get_groq():
    """Lazily initialize Groq client on first use."""
    global _groq_llm
    if _groq_llm is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set in environment")
        _groq_llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=api_key,
            temperature=0.7,
            max_tokens=300,
        )
        logger.info("Groq LLM initialized (llama-3.3-70b-versatile)")
    return _groq_llm


def _get_gemini():
    """Lazily initialize Gemini client on first use."""
    global _gemini_llm
    if _gemini_llm is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set in environment")
        _gemini_llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            google_api_key=api_key,
            temperature=0.7,
            max_output_tokens=300,
        )
        logger.info("Gemini LLM initialized (gemini-1.5-flash-latest)")
    return _gemini_llm


# ── Public router ──────────────────────────────────────────────────

async def get_llm_response(
    system_prompt: str,
    user_message: str,
    call_id: str = None,
) -> dict:
    """
    Smart LLM router: tries Groq first (fastest), falls back to Gemini.
    Returns: {"text": str, "provider": str, "success": bool}
    """
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]

    # Try Groq first (primary — ~500 tok/s)
    try:
        groq = _get_groq()
        response = await groq.ainvoke(messages)
        return {
            "text": response.content,
            "provider": "groq",
            "success": True,
        }
    except Exception as groq_error:
        logger.warning("Groq failed: %s. Switching to Gemini.", groq_error)

    # Fallback to Gemini
    try:
        gemini = _get_gemini()
        response = await gemini.ainvoke(messages)
        return {
            "text": response.content,
            "provider": "gemini",
            "success": True,
        }
    except Exception as gemini_error:
        logger.error("Both LLMs failed. Gemini error: %s", gemini_error)
        return {
            "text": "I apologize, I'm having trouble responding. Our team will call you back shortly.",
            "provider": "none",
            "success": False,
        }
