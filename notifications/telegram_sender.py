from __future__ import annotations

import httpx

from app.config import settings


class TelegramSender:
    BASE_URL = "https://api.telegram.org/bot{token}/sendMessage"

    def send_message(self, text: str, chat_id: str | None = None) -> dict:
        token = settings.telegram_bot_token
        target_chat = chat_id or settings.telegram_chat_id

        if not token or not target_chat:
            raise ValueError("TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID são obrigatórios.")

        url = self.BASE_URL.format(token=token)
        payload = {
            "chat_id": target_chat,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
