from __future__ import annotations

import httpx

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"


def generate_text(
    *,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.4,
) -> str:
    url = f"{GEMINI_API_URL}/{model}:generateContent"
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {"temperature": temperature},
    }

    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            url,
            params={"key": api_key},
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    candidates = data.get("candidates") or []
    if not candidates:
        raise ValueError("Gemini retornou resposta vazia")

    parts = candidates[0].get("content", {}).get("parts") or []
    text_parts = [part.get("text", "") for part in parts if part.get("text")]
    content = "".join(text_parts).strip()
    if not content:
        raise ValueError("Gemini retornou texto vazio")

    return content
