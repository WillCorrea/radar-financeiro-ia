from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from agents.gemini_client import format_http_error, generate_text
from agents.summary_agent import SummaryAgent


def _mock_response(status_code: int, *, json_data: dict | None = None, headers: dict | None = None) -> httpx.Response:
    request = httpx.Request("POST", "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent")
    return httpx.Response(status_code, request=request, json=json_data or {}, headers=headers or {})


def test_generate_text_retries_on_429_then_succeeds() -> None:
    success_payload = {
        "candidates": [{"content": {"parts": [{"text": "Resumo gerado."}]}}],
    }
    client = MagicMock()
    client.post.side_effect = [
        _mock_response(429),
        _mock_response(200, json_data=success_payload),
    ]

    with patch("agents.gemini_client.httpx.Client") as mock_client_cls, patch("agents.gemini_client.time.sleep"):
        mock_client_cls.return_value.__enter__.return_value = client
        result = generate_text(
            api_key="secret",
            model="gemini-2.0-flash",
            system_prompt="sys",
            user_prompt="user",
            max_retries=2,
            retry_base_seconds=0.01,
        )

    assert result == "Resumo gerado."
    assert client.post.call_count == 2


def test_generate_text_raises_after_exhausted_retries() -> None:
    client = MagicMock()
    client.post.return_value = _mock_response(429)

    with patch("agents.gemini_client.httpx.Client") as mock_client_cls, patch("agents.gemini_client.time.sleep"):
        mock_client_cls.return_value.__enter__.return_value = client
        with pytest.raises(httpx.HTTPStatusError):
            generate_text(
                api_key="secret",
                model="gemini-2.0-flash",
                system_prompt="sys",
                user_prompt="user",
                max_retries=1,
                retry_base_seconds=0.01,
            )

    assert client.post.call_count == 2


def test_format_http_error_sanitizes_429() -> None:
    request = httpx.Request(
        "POST",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=secret",
    )
    response = httpx.Response(429, request=request)
    exc = httpx.HTTPStatusError("boom", request=request, response=response)

    message = format_http_error(exc)

    assert "secret" not in message
    assert "429" in message


def test_summary_agent_uses_fallback_on_gemini_429(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("agents.summary_agent.settings.gemini_api_key", "valid-key")
    monkeypatch.setattr("agents.summary_agent.settings.llm_provider", "gemini")
    monkeypatch.setattr("agents.summary_agent.settings.debug", False)

    request = httpx.Request("POST", "https://example.com")
    response = httpx.Response(429, request=request)
    error = httpx.HTTPStatusError("429", request=request, response=response)

    with patch("agents.summary_agent.generate_gemini_text", side_effect=error):
        summary = SummaryAgent().generate_daily_summary(["PETR4 caiu 3.2% na semana."])

    assert summary.startswith("Resumo automático")
    assert "PETR4 caiu 3.2% na semana." in summary
