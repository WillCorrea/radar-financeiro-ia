from __future__ import annotations

from app.config import Settings


def test_settings_strips_crlf_from_env_values() -> None:
    settings = Settings.model_validate({"debug": "true\r", "gemini_api_key": "abc\r\n"})

    assert settings.debug is True
    assert settings.gemini_api_key == "abc"
