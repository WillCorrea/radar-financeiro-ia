from __future__ import annotations

from sqlalchemy.orm import Session

from analyzers.event_analyzer import EventAnalyzer, EventHighlight
from app.config import settings
from collectors.dividends_collector import DividendsCollector
from collectors.events_collector import EventsCollector
from database.models import Alert, Asset, MessageSent, User
from notifications.telegram_sender import TelegramSender


class EventsJob:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.dividends_collector = DividendsCollector()
        self.events_collector = EventsCollector()
        self.event_analyzer = EventAnalyzer()
        self.telegram_sender = TelegramSender()

    def run(self, user_email: str | None = None) -> str | None:
        user = self._get_user(user_email)
        tickers = self._resolve_tickers(user)
        stock_tickers, fii_tickers = self._split_tickers(tickers)
        all_tickers = stock_tickers + fii_tickers

        dividends = self.dividends_collector.fetch_events(all_tickers)
        corporate_events = self.events_collector.fetch_events(stock_tickers)

        highlights = self.event_analyzer.build_highlights(dividends, corporate_events, self.db)
        if not highlights:
            return None

        message = self._build_message(highlights)
        self._persist(user, highlights, message)

        chat_id = user.telegram_chat_id or settings.telegram_chat_id
        self.telegram_sender.send_message(message, chat_id=chat_id)

        return message

    def _get_user(self, user_email: str | None) -> User:
        query = self.db.query(User)
        if user_email:
            user = query.filter(User.email == user_email).first()
            if not user:
                raise ValueError(f"Usuário não encontrado: {user_email}")
            return user

        user = query.first()
        if not user:
            user = User(
                name="Usuário MVP",
                email="mvp@radar.local",
                telegram_chat_id=settings.telegram_chat_id or None,
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        return user

    def _resolve_tickers(self, user: User) -> list[str]:
        user_tickers = [ua.asset.ticker for ua in user.assets if ua.asset]
        if user_tickers:
            return user_tickers
        return settings.asset_list

    def _split_tickers(self, tickers: list[str]) -> tuple[list[str], list[str]]:
        fii_tickers = [t for t in tickers if t.endswith("11")]
        stock_tickers = [t for t in tickers if not t.endswith("11")]
        return stock_tickers, fii_tickers

    def _build_message(self, highlights: list[EventHighlight]) -> str:
        lines = ["<b>Alerta — Eventos</b>", ""]

        for item in highlights:
            lines.append(_format_highlight_bullet(item.message))

        return "\n".join(lines)

    def _persist(self, user: User, highlights: list[EventHighlight], message: str) -> None:
        for item in highlights:
            asset = self._get_or_create_asset(item.ticker)
            alert = Alert(
                asset_id=asset.id,
                alert_type=item.alert_type,
                title=item.title,
                content=item.message,
                fingerprint=item.fingerprint,
            )
            self.db.add(alert)

        sent = MessageSent(user_id=user.id, channel="telegram", content=message)
        self.db.add(sent)
        self.db.commit()

    def _get_or_create_asset(self, ticker: str) -> Asset:
        asset = self.db.query(Asset).filter(Asset.ticker == ticker).first()
        if asset:
            return asset

        asset_type = "fii" if ticker.endswith("11") else "stock"
        asset = Asset(ticker=ticker, asset_type=asset_type)
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset


def _format_highlight_bullet(message: str) -> str:
    lines = message.split("\n")
    if not lines:
        return ""

    formatted = f"• {lines[0]}"
    for line in lines[1:]:
        formatted = f"{formatted}\n  {line}"
    return formatted
