from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from agents.summary_agent import SummaryAgent
from analyzers.price_analyzer import PriceAnalyzer
from app.config import settings
from collectors.fii_collector import FiiCollector
from collectors.stocks_collector import QuoteData, StocksCollector
from database.models import Alert, Asset, MarketSnapshot, MessageSent, User
from notifications.telegram_sender import TelegramSender


class DailyRadarJob:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.stocks_collector = StocksCollector()
        self.fii_collector = FiiCollector()
        self.price_analyzer = PriceAnalyzer()
        self.summary_agent = SummaryAgent()
        self.telegram_sender = TelegramSender()

    def run(self, user_email: str | None = None) -> str:
        user = self._get_user(user_email)
        tickers = self._resolve_tickers(user)
        stock_tickers, fii_tickers = self._split_tickers(tickers)

        quotes: list[QuoteData] = []
        quotes.extend(self.stocks_collector.fetch_quotes(stock_tickers))
        quotes.extend(self.fii_collector.fetch_quotes(fii_tickers))

        highlights = self.price_analyzer.build_highlights(quotes)
        ai_summary = self.summary_agent.generate_daily_summary([h.message for h in highlights])

        message = self._build_message(highlights, ai_summary)
        self._persist(user, quotes, highlights, ai_summary, message)

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

    def _build_message(self, highlights, ai_summary: str) -> str:
        today = datetime.now().strftime("%d/%m/%Y")
        lines = [f"<b>Radar Financeiro - {today}</b>", ""]

        for item in highlights:
            lines.append(f"• {item.message}")

        lines.extend(["", "<b>Resumo IA:</b>", ai_summary])
        return "\n".join(lines)

    def _persist(self, user: User, quotes, highlights, ai_summary: str, message: str) -> None:
        for quote in quotes:
            asset = self._get_or_create_asset(quote)
            snapshot = MarketSnapshot(
                asset_id=asset.id,
                price=quote.price,
                change_percent_day=quote.change_percent_day,
                change_percent_week=quote.change_percent_week,
                change_percent_month=quote.change_percent_month,
            )
            self.db.add(snapshot)

        for item in highlights:
            asset = self.db.query(Asset).filter(Asset.ticker == item.ticker).first()
            alert = Alert(
                asset_id=asset.id if asset else None,
                alert_type="price_highlight",
                title=f"Destaque {item.ticker}",
                content=item.message,
            )
            self.db.add(alert)

        summary_alert = Alert(
            asset_id=None,
            alert_type="daily_summary",
            title="Resumo diário",
            content=ai_summary,
        )
        self.db.add(summary_alert)

        sent = MessageSent(user_id=user.id, channel="telegram", content=message)
        self.db.add(sent)
        self.db.commit()

    def _get_or_create_asset(self, quote: QuoteData) -> Asset:
        asset = self.db.query(Asset).filter(Asset.ticker == quote.ticker).first()
        if asset:
            return asset

        asset_type = "fii" if quote.ticker.endswith("11") else "stock"
        asset = Asset(ticker=quote.ticker, asset_type=asset_type, name=quote.name)
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset
