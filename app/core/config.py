
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Business Intelligence Platform"
    database_url: str = "sqlite:///./business_intelligence.db"

    # Gemini configuration
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    enable_llm: bool = False

    secret_key: str | None = None
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
