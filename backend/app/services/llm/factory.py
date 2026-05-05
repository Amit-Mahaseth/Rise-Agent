from types import SimpleNamespace
from typing import Any

from app.core.config import Settings


class OfflineChatModel:
    def invoke(self, _: Any) -> SimpleNamespace:
        return SimpleNamespace(
            content=(
                "Thank you for sharing that. I can help with Rupeezy loan options, "
                "eligibility, documents, and next steps. Would you like me to explain the process or send a follow-up link?"
            )
        )


def build_chat_model(settings: Settings) -> Any:
    provider = settings.llm_provider.lower()

    if provider == "anthropic" and settings.anthropic_api_key:
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=settings.llm_model,
            anthropic_api_key=settings.anthropic_api_key,
            temperature=0.2,
            max_tokens=500,
        )

    if provider == "mistral" and settings.mistral_api_key:
        from langchain_mistralai import ChatMistralAI

        return ChatMistralAI(
            model=settings.llm_model,
            api_key=settings.mistral_api_key,
            temperature=0.2,
            max_tokens=500,
        )

    return OfflineChatModel()

