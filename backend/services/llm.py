import os
import logging
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

groq_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7,
    max_tokens=300
)

gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7,
    max_output_tokens=300
)

async def get_llm_response(
    system_prompt: str,
    user_message: str,
    call_id: str = None
) -> dict:
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    # Try Groq first
    try:
        response = await groq_llm.ainvoke(messages)
        return {
            "text": response.content,
            "provider": "groq",
            "success": True
        }
    except Exception as groq_error:
        logger.warning(f"Groq failed: {groq_error}. Switching to Gemini.")

    # Fallback to Gemini
    try:
        response = await gemini_llm.ainvoke(messages)
        return {
            "text": response.content,
            "provider": "gemini",
            "success": True
        }
    except Exception as gemini_error:
        logger.error(f"Both LLMs failed. Gemini error: {gemini_error}")
        return {
            "text": "I apologize, I'm having trouble responding. Our team will call you back shortly.",
            "provider": "none",
            "success": False
        }
