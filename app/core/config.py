from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration comes from environment variables (see .env.example)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "stallo-api"
    environment: str = "local"  # local | staging | production
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173"]
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://stallo:stallo@localhost:5432/stallo"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    # WhatsApp linked-device provider (Evolution API / WAHA)
    whatsapp_api_base_url: str = "http://localhost:8080"
    whatsapp_api_key: str = ""
    whatsapp_webhook_secret: str = ""

    # Payments
    paystack_secret_key: str = ""
    hubtel_client_id: str = ""
    hubtel_client_secret: str = ""

    # LLM
    llm_provider: str = "anthropic"
    llm_api_key: str = ""
    llm_model: str = ""
    llm_confidence_threshold: float = 0.75

    # Outbound pacing (messages per second per seller session)
    outbound_rate_per_second: float = 1.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
