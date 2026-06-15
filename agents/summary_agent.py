from __future__ import annotations

from datetime import date

import httpx
from openai import OpenAI

from agents.gemini_client import generate_text as generate_gemini_text
from app.config import settings

SYSTEM_PROMPT = "Responda em português do Brasil."


class SummaryAgent:
    def __init__(self) -> None:
        self._openai_client = (
            OpenAI(api_key=settings.openai_api_key.strip())
            if settings.openai_api_key_configured
            else None
        )

    def generate_daily_summary(self, highlights: list[str]) -> str:
        if not highlights:
            return "Nenhum destaque relevante encontrado para os ativos monitorados hoje."

        prompt = self._build_prompt(highlights)
        provider = settings.llm_provider.strip().lower()

        try:
            if provider == "gemini" and settings.gemini_api_key_configured:
                return self._generate_with_gemini(prompt)
            if provider == "openai" and self._openai_client:
                return self._generate_with_openai(prompt)
        except (httpx.HTTPError, ValueError) as exc:
            if settings.debug:
                print(f"[SummaryAgent] Falha no provedor {provider}: {exc}")

        return self._fallback_summary(highlights)

    def _build_prompt(self, highlights: list[str]) -> str:
        return (
            "Você é um assistente financeiro informativo. "
            "Não recomende compra ou venda. "
            "Resuma os destaques abaixo em até 3 frases, linguagem simples, tom neutro.\n\n"
            + "\n".join(f"- {item}" for item in highlights)
        )

    def _generate_with_gemini(self, prompt: str) -> str:
        return generate_gemini_text(
            api_key=settings.gemini_api_key.strip(),
            model=settings.gemini_model,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=prompt,
            temperature=0.4,
        )

    def _generate_with_openai(self, prompt: str) -> str:
        if not self._openai_client:
            raise ValueError("OpenAI não configurada")

        response = self._openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )

        content = response.choices[0].message.content
        if not content or not content.strip():
            raise ValueError("OpenAI retornou texto vazio")

        return content.strip()

    def _fallback_summary(self, highlights: list[str]) -> str:
        joined = " ".join(highlights[:3])
        return (
            f"Resumo automático ({date.today():%d/%m/%Y}): "
            f"mercado com movimentos mistos. Destaques: {joined}"
        )
