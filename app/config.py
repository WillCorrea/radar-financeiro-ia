from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    debug: bool = True

    database_url: str = "postgresql://radar:radar@localhost:5433/radar_financeiro"

    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    brapi_token: str = ""

    brapi_request_delay_seconds: float = 0.2

    monitored_assets: str = "PETR4,VALE3,HGLG11,MXRF11"

    radar_schedule_hour: int = 18
    radar_schedule_minute: int = 30

    @property
    def brapi_token_configured(self) -> bool:
        return _is_configured_secret(self.brapi_token, {"your-brapi-token-here", "seu-token-aqui", "changeme"})

    @property
    def gemini_api_key_configured(self) -> bool:
        return _is_configured_secret(self.gemini_api_key, {"your-gemini-api-key-here", "seu-token-aqui", "changeme"})

    @property
    def openai_api_key_configured(self) -> bool:
        return _is_configured_secret(
            self.openai_api_key,
            {"sk-your-key-here", "your-openai-key-here", "changeme"},
        )

    @property
    def asset_list(self) -> list[str]:
        return [asset.strip().upper() for asset in self.monitored_assets.split(",") if asset.strip()]


settings = Settings()


def _is_configured_secret(value: str, placeholders: set[str]) -> bool:
    token = value.strip()
    if not token:
        return False
    return token.lower() not in placeholders
