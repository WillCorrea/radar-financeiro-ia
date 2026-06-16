from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from analyzers.event_analyzer import (
    ALERT_TYPE_CORPORATE,
    ALERT_TYPE_DIVIDEND,
    ALERT_TYPE_JCP,
    EventAnalyzer,
)
from collectors.dividends_collector import DividendEvent
from collectors.events_collector import CorporateEvent
from database.models import Alert, Asset, Base


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


@pytest.fixture
def analyzer() -> EventAnalyzer:
    return EventAnalyzer()


def test_dividend_highlight_format(analyzer: EventAnalyzer, db_session: Session) -> None:
    highlights = analyzer.build_highlights(
        [
            DividendEvent(
                ticker="PETR4",
                event_type="dividend",
                amount_per_share=1.25,
                ex_date=date(2026, 8, 15),
                payment_date=date(2026, 8, 30),
            )
        ],
        [],
        db_session,
    )

    assert len(highlights) == 1
    highlight = highlights[0]
    assert highlight.ticker == "PETR4"
    assert highlight.alert_type == ALERT_TYPE_DIVIDEND
    assert "PETR4 anunciou dividendos de R$ 1,25 por ação." in highlight.message
    assert "Data-base: 15/08/2026 | Pagamento: 30/08/2026" in highlight.message


def test_jcp_highlight_uses_jcp_alert_type(analyzer: EventAnalyzer, db_session: Session) -> None:
    highlights = analyzer.build_highlights(
        [
            DividendEvent(
                ticker="VALE3",
                event_type="jcp",
                amount_per_share=0.8,
                ex_date=date(2026, 6, 10),
                payment_date=date(2026, 6, 25),
            )
        ],
        [],
        db_session,
    )

    assert highlights[0].alert_type == ALERT_TYPE_JCP
    assert "JCP" in highlights[0].message


def test_corporate_event_highlight(analyzer: EventAnalyzer, db_session: Session) -> None:
    highlights = analyzer.build_highlights(
        [],
        [
            CorporateEvent(
                ticker="PETR4",
                title="Aquisição de participação societária",
                published_at=date(2026, 6, 10),
                source_url="https://cvm.example/doc.pdf",
            )
        ],
        db_session,
    )

    assert len(highlights) == 1
    assert highlights[0].alert_type == ALERT_TYPE_CORPORATE
    assert "fato relevante" in highlights[0].message
    assert "https://cvm.example/doc.pdf" in highlights[0].message


def test_dedup_skips_existing_fingerprint(analyzer: EventAnalyzer, db_session: Session) -> None:
    event = DividendEvent(
        ticker="PETR4",
        event_type="dividend",
        amount_per_share=1.25,
        ex_date=date(2026, 8, 15),
        payment_date=date(2026, 8, 30),
    )
    first = analyzer.build_highlights([event], [], db_session)
    assert len(first) == 1

    asset = Asset(ticker="PETR4", asset_type="stock")
    db_session.add(asset)
    db_session.flush()
    db_session.add(
        Alert(
            asset_id=asset.id,
            alert_type=ALERT_TYPE_DIVIDEND,
            title="Dividendo PETR4",
            content=first[0].message,
            fingerprint=first[0].fingerprint,
        )
    )
    db_session.commit()

    second = analyzer.build_highlights([event], [], db_session)
    assert second == []


def test_filters_events_outside_lookback(
    analyzer: EventAnalyzer,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FixedToday:
        @staticmethod
        def today() -> date:
            return date(2026, 6, 15)

    monkeypatch.setattr("analyzers.event_analyzer.date", FixedToday)

    highlights = analyzer.build_highlights(
        [
            DividendEvent(
                ticker="PETR4",
                event_type="dividend",
                amount_per_share=1.0,
                ex_date=date(2026, 1, 1),
                payment_date=date(2026, 1, 15),
            )
        ],
        [],
        db_session,
    )

    assert highlights == []
