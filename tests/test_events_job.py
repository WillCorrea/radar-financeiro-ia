from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from analyzers.event_analyzer import ALERT_TYPE_DIVIDEND, EventHighlight
from collectors.dividends_collector import DividendEvent
from database.models import Alert, Base, MessageSent, User
from jobs.events_job import EventsJob, _format_highlight_bullet


@pytest.fixture
def job() -> EventsJob:
    return EventsJob(db=MagicMock())


def test_format_highlight_bullet() -> None:
    message = "PETR4 anunciou dividendos de R$ 1,25 por ação.\nData-base: 15/08/2026 | Pagamento: 30/08/2026"
    formatted = _format_highlight_bullet(message)

    assert formatted.startswith("• PETR4 anunciou dividendos")
    assert "\n  Data-base: 15/08/2026 | Pagamento: 30/08/2026" in formatted


def test_build_message_format(job: EventsJob) -> None:
    highlights = [
        EventHighlight(
            ticker="PETR4",
            alert_type=ALERT_TYPE_DIVIDEND,
            message="PETR4 anunciou dividendos de R$ 1,25 por ação.\nData-base: 15/08/2026 | Pagamento: 30/08/2026",
            fingerprint="PETR4|dividend|2026-08-15|2026-08-30|1.2500",
            title="Dividendo PETR4",
        )
    ]

    message = job._build_message(highlights)

    assert message.startswith("<b>Alerta — Eventos</b>")
    assert "• PETR4 anunciou dividendos de R$ 1,25 por ação." in message
    assert "  Data-base: 15/08/2026 | Pagamento: 30/08/2026" in message


@patch("jobs.events_job.TelegramSender")
@patch("jobs.events_job.EventAnalyzer")
@patch("jobs.events_job.EventsCollector")
@patch("jobs.events_job.DividendsCollector")
def test_run_returns_none_without_new_events(
    mock_dividends_cls: MagicMock,
    mock_events_cls: MagicMock,
    mock_analyzer_cls: MagicMock,
    mock_telegram_cls: MagicMock,
) -> None:
    mock_dividends_cls.return_value.fetch_events.return_value = []
    mock_events_cls.return_value.fetch_events.return_value = []
    mock_analyzer_cls.return_value.build_highlights.return_value = []

    db = MagicMock()
    user = MagicMock()
    user.telegram_chat_id = "123"
    user.assets = []
    db.query.return_value.first.return_value = user

    job = EventsJob(db)
    with patch.object(job, "_resolve_tickers", return_value=["PETR4"]):
        result = job.run()

    assert result is None
    mock_telegram_cls.return_value.send_message.assert_not_called()


@patch("jobs.events_job.TelegramSender")
@patch("jobs.events_job.EventAnalyzer")
@patch("jobs.events_job.EventsCollector")
@patch("jobs.events_job.DividendsCollector")
def test_run_sends_telegram_with_new_events(
    mock_dividends_cls: MagicMock,
    mock_events_cls: MagicMock,
    mock_analyzer_cls: MagicMock,
    mock_telegram_cls: MagicMock,
) -> None:
    dividend = DividendEvent(
        ticker="PETR4",
        event_type="dividend",
        amount_per_share=1.25,
        ex_date=date(2026, 8, 15),
        payment_date=date(2026, 8, 30),
    )
    highlight = EventHighlight(
        ticker="PETR4",
        alert_type=ALERT_TYPE_DIVIDEND,
        message="PETR4 anunciou dividendos de R$ 1,25 por ação.\nData-base: 15/08/2026 | Pagamento: 30/08/2026",
        fingerprint="PETR4|dividend|2026-08-15|2026-08-30|1.2500",
        title="Dividendo PETR4",
    )

    mock_dividends_cls.return_value.fetch_events.return_value = [dividend]
    mock_events_cls.return_value.fetch_events.return_value = []
    mock_analyzer_cls.return_value.build_highlights.return_value = [highlight]
    mock_telegram = mock_telegram_cls.return_value

    db = MagicMock()
    user = MagicMock()
    user.telegram_chat_id = "123"
    user.assets = []
    db.query.return_value.first.return_value = user

    job = EventsJob(db)
    with patch.object(job, "_resolve_tickers", return_value=["PETR4"]), patch.object(job, "_persist"):
        message = job.run()

    mock_dividends_cls.return_value.fetch_events.assert_called_once_with(["PETR4"])
    mock_events_cls.return_value.fetch_events.assert_called_once_with(["PETR4"])
    mock_telegram.send_message.assert_called_once()
    sent_text = mock_telegram.send_message.call_args[0][0]
    sent_chat_id = mock_telegram.send_message.call_args[0][1] if len(mock_telegram.send_message.call_args[0]) > 1 else mock_telegram.send_message.call_args.kwargs.get("chat_id")
    assert sent_chat_id == "123"
    assert sent_text.startswith("<b>Alerta — Eventos</b>")
    assert "• PETR4 anunciou dividendos de R$ 1,25 por ação." in sent_text
    assert "  Data-base: 15/08/2026 | Pagamento: 30/08/2026" in sent_text
    assert message is not None
    assert "<b>Alerta — Eventos</b>" in message
    assert "PETR4" in message


@patch("jobs.events_job.TelegramSender")
def test_second_run_dedup_skips_telegram(mock_telegram_cls: MagicMock, db_session: Session) -> None:
    user = User(name="Test", email="dedup@example.com", telegram_chat_id="999")
    db_session.add(user)
    db_session.commit()

    dividend = DividendEvent(
        ticker="PETR4",
        event_type="dividend",
        amount_per_share=1.25,
        ex_date=date(2026, 8, 15),
        payment_date=date(2026, 8, 30),
    )

    job = EventsJob(db_session)
    job.dividends_collector = MagicMock()
    job.events_collector = MagicMock()
    job.dividends_collector.fetch_events.return_value = [dividend]
    job.events_collector.fetch_events.return_value = []

    mock_telegram = mock_telegram_cls.return_value

    with patch.object(job, "_resolve_tickers", return_value=["PETR4"]):
        first = job.run()
        second = job.run()

    assert first is not None
    assert second is None
    mock_telegram.send_message.assert_called_once()
    assert db_session.query(Alert).count() == 1
    assert db_session.query(MessageSent).count() == 1


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def test_persist_saves_alerts_with_fingerprint(db_session: Session) -> None:
    user = User(name="Test", email="test@example.com", telegram_chat_id="1")
    db_session.add(user)
    db_session.commit()

    job = EventsJob(db_session)
    highlights = [
        EventHighlight(
            ticker="PETR4",
            alert_type=ALERT_TYPE_DIVIDEND,
            message="PETR4 anunciou dividendos de R$ 1,25 por ação.",
            fingerprint="PETR4|dividend|2026-08-15|2026-08-30|1.2500",
            title="Dividendo PETR4",
        )
    ]
    job._persist(user, highlights, "<b>Alerta — Eventos</b>")

    alerts = db_session.query(Alert).all()
    messages = db_session.query(MessageSent).all()

    assert len(alerts) == 1
    assert alerts[0].alert_type == ALERT_TYPE_DIVIDEND
    assert alerts[0].fingerprint == "PETR4|dividend|2026-08-15|2026-08-30|1.2500"
    assert len(messages) == 1
    assert messages[0].channel == "telegram"
