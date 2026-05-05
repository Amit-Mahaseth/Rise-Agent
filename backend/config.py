"""
RiseAgent AI — Centralised configuration.
All environment variables are validated at import time so the app
fails fast if anything critical is missing.
"""

from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    # ── LLMs ─────────────────────────────────────────────────────
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")

    # ── Sarvam AI ────────────────────────────────────────────────
    sarvam_api_key: str = Field(default="", alias="SARVAM_API_KEY")

    # ── Exotel ───────────────────────────────────────────────────
    exotel_api_key: str = Field(default="", alias="EXOTEL_API_KEY")
    exotel_api_token: str = Field(default="", alias="EXOTEL_API_TOKEN")
    exotel_sid: str = Field(default="", alias="EXOTEL_SID")
    exotel_caller_id: str = Field(default="", alias="EXOTEL_CALLER_ID")

    # ── Twilio (fallback) ────────────────────────────────────────
    twilio_account_sid: str = Field(default="", alias="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = Field(default="", alias="TWILIO_AUTH_TOKEN")
    twilio_phone_number: str = Field(default="", alias="TWILIO_PHONE_NUMBER")

    # ── Call provider switch ─────────────────────────────────────
    call_provider: str = Field(default="exotel", alias="CALL_PROVIDER")

    # ── Supabase ─────────────────────────────────────────────────
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_service_key: str = Field(default="", alias="SUPABASE_SERVICE_KEY")

    # ── WhatsApp Meta Cloud ──────────────────────────────────────
    whatsapp_token: str = Field(default="", alias="WHATSAPP_TOKEN")
    whatsapp_phone_number_id: str = Field(default="", alias="WHATSAPP_PHONE_NUMBER_ID")

    # ── Application ──────────────────────────────────────────────
    base_url: str = Field(default="http://localhost:8000", alias="BASE_URL")
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")
    port: int = Field(default=8000, alias="PORT")

    # ── Demo mode ────────────────────────────────────────────────
    demo_mode: bool = Field(default=True, alias="DEMO_MODE")

    # ── Paths ────────────────────────────────────────────────────
    project_root: Path = Path(__file__).resolve().parent
    chroma_persist_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent / "chroma_data")
    knowledge_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent / "knowledge")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True
        extra = "ignore"

    def model_post_init(self, __context) -> None:
        # Ensure chroma persistence directory exists
        self.chroma_persist_dir.mkdir(parents=True, exist_ok=True)

    # ── Validation helpers ───────────────────────────────────────
    def validate_required(self) -> list[str]:
        """Return list of missing but required env vars."""
        missing: list[str] = []
        if self.demo_mode:
            # In demo mode we only need Groq + Gemini + Sarvam
            if not self.groq_api_key:
                missing.append("GROQ_API_KEY")
            if not self.gemini_api_key:
                missing.append("GEMINI_API_KEY")
            if not self.sarvam_api_key:
                missing.append("SARVAM_API_KEY")
        else:
            required_fields = {
                "GROQ_API_KEY": self.groq_api_key,
                "GEMINI_API_KEY": self.gemini_api_key,
                "SARVAM_API_KEY": self.sarvam_api_key,
                "SUPABASE_URL": self.supabase_url,
                "SUPABASE_SERVICE_KEY": self.supabase_service_key,
            }
            if self.call_provider == "exotel":
                required_fields.update({
                    "EXOTEL_API_KEY": self.exotel_api_key,
                    "EXOTEL_API_TOKEN": self.exotel_api_token,
                    "EXOTEL_SID": self.exotel_sid,
                    "EXOTEL_CALLER_ID": self.exotel_caller_id,
                })
            elif self.call_provider == "twilio":
                required_fields.update({
                    "TWILIO_ACCOUNT_SID": self.twilio_account_sid,
                    "TWILIO_AUTH_TOKEN": self.twilio_auth_token,
                    "TWILIO_PHONE_NUMBER": self.twilio_phone_number,
                })
            for name, value in required_fields.items():
                if not value:
                    missing.append(name)
        return missing


@lru_cache()
def get_settings() -> Settings:
    """Singleton accessor for Settings."""
    return Settings()
