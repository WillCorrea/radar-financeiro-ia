from __future__ import annotations

import time

import httpx

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


def generate_text(
    *,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.4,
    max_retries: int = 3,
    retry_base_seconds: float = 2.0,
) -> str:
    url = f"{GEMINI_API_URL}/{model}:generateContent"
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {"temperature": temperature},
    }

    with httpx.Client(timeout=60.0) as client:
        response = _post_with_retries(
            client,
            url=url,
            api_key=api_key,
            payload=payload,
            max_retries=max_retries,
            retry_base_seconds=retry_base_seconds,
        )
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


def _post_with_retries(
    client: httpx.Client,
    *,
    url: str,
    api_key: str,
    payload: dict,
    max_retries: int,
    retry_base_seconds: float,
) -> httpx.Response:
    last_response: httpx.Response | None = None

    for attempt in range(max_retries + 1):
        response = client.post(url, params={"key": api_key}, json=payload)
        last_response = response

        if response.status_code not in RETRYABLE_STATUS_CODES:
            response.raise_for_status()
            return response

        if attempt >= max_retries:
            response.raise_for_status()

        wait_seconds = _retry_wait_seconds(response, attempt, retry_base_seconds)
        time.sleep(wait_seconds)

    if last_response is not None:
        last_response.raise_for_status()

    raise httpx.HTTPError("Gemini request failed without response")


def _retry_wait_seconds(response: httpx.Response, attempt: int, retry_base_seconds: float) -> float:
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return max(float(retry_after), 0.0)
        except ValueError:
            pass

    return retry_base_seconds * (2**attempt)


def format_http_error(exc: httpx.HTTPError) -> str:
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        if status == 429:
            return "HTTP 429 (limite de requisições do Gemini — aguarde ou use o resumo automático)"
        return f"HTTP {status}"

    message = str(exc)
    if "for url" in message:
        message = message.split("for url", 1)[0].strip()
    return message
