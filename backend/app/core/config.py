"""
Configuration management for RiseAgent AI.
"""

import secrets
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Basic app configuration
    app_name: str = Field(default="RiseAgent AI", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")

    # Authentication and server settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str = "RiseAgent AI"
    SERVER_HOST: AnyHttpUrl = "http://localhost"
    DEBUG: bool = True

    # CORS configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value: str | list[str]) -> str | list[str]:
        if isinstance(value, str) and not value.startswith("["):
            return [item.strip() for item in value.split(",")]
        return value

    @field_validator("DEBUG", mode="before")
    @classmethod
    def coerce_debug(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug", "development"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "prod", "production"}:
                return False
        return bool(value)

    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Database configuration
    database_url: str = Field(default="sqlite:///./riseagent.db", alias="DATABASE_URL")
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "riseagent"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "riseagent"
    POSTGRES_PORT: int = 5432

    # Cache and queue configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL: int = 3600

    # LLM configuration
    llm_provider: str = Field(default="anthropic", alias="LLM_PROVIDER")
    llm_model: str = Field(default="claude-3-5-sonnet-latest", alias="LLM_MODEL")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    mistral_api_key: str | None = Field(default=None, alias="MISTRAL_API_KEY")

    # Sarvam configuration
    sarvam_api_key: str | None = Field(default=None, alias="SARVAM_API_KEY")
    sarvam_base_url: str = Field(default="https://api.sarvam.ai", alias="SARVAM_BASE_URL")
    sarvam_tts_endpoint: str = Field(default="/text-to-speech", alias="SARVAM_TTS_ENDPOINT")

    # Twilio configuration
    twilio_account_sid: str | None = Field(default=None, alias="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str | None = Field(default=None, alias="TWILIO_AUTH_TOKEN")
    twilio_voice_from: str | None = Field(default=None, alias="TWILIO_VOICE_FROM")
    twilio_whatsapp_from: str = Field(
        default="whatsapp:+14155238886",
        alias="TWILIO_WHATSAPP_FROM",
    )

    # Vector and knowledge configuration
    chroma_path: str = Field(default="./data/chroma", alias="CHROMA_PATH")
    knowledge_base_dir: str = Field(default="./data", alias="KNOWLEDGE_BASE_DIR")
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_DOCUMENTS: int = 4

    # Scoring and language configuration
    HOT_LEAD_THRESHOLD: float = 0.8
    WARM_LEAD_THRESHOLD: float = 0.5
    MIN_CONVERSATION_LENGTH: int = 30
    MAX_CONVERSATION_LENGTH: int = 600
    SUPPORTED_LANGUAGES: List[str] = [
        "Hindi",
        "English",
        "Hinglish",
        "Marathi",
        "Tamil",
        "Telugu",
        "Gujarati",
        "Bengali",
    ]

    # URLs and webhooks
    public_base_url: str = Field(default="http://localhost:8000", alias="PUBLIC_BASE_URL")
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")
    rm_handoff_webhook: str | None = Field(default=None, alias="RM_HANDOFF_WEBHOOK")
    warm_followup_url: str = Field(
        default="https://rupeezy.example.com/apply",
        alias="WARM_FOLLOWUP_URL",
    )

    # Security and logging
    ENCRYPTION_KEY: str = secrets.token_hex(32)
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    SENTRY_DSN: str | None = None
    ENABLE_METRICS: bool = True
    enable_tuning_debug: bool = Field(default=False, alias="ENABLE_TUNING_DEBUG")

    # Agent persona for voice tone.
    agent_persona: str = Field(default="professional", alias="AGENT_PERSONA")

    # Auxiliary paths
    SCRIPTS_PATH: str = "./data/scripts"
    FAQ_PATH: str = "./data/faq"
    UPLOADS_PATH: str = "./uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def chroma_dir(self) -> Path:
        return (self.project_root / self.chroma_path).resolve()

    @property
    def knowledge_dir(self) -> Path:
        return (self.project_root / self.knowledge_base_dir).resolve()


settings = Settings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
