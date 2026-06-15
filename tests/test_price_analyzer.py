from __future__ import annotations

import pytest

from analyzers.price_analyzer import PriceAnalyzer
from collectors.stocks_collector import QuoteData


@pytest.fixture
def analyzer() -> PriceAnalyzer:
    return PriceAnalyzer()


def _quote(**kwargs: object) -> QuoteData:
    defaults = {
        "ticker": "PETR4",
        "price": 30.0,
        "change_percent_day": 0.5,
        "change_percent_week": 1.0,
        "change_percent_month": 1.5,
    }
    defaults.update(kwargs)
    return QuoteData(**defaults)


def test_prioritizes_month_over_week_and_day(analyzer: PriceAnalyzer) -> None:
    quote = _quote(change_percent_month=4.0, change_percent_week=3.0, change_percent_day=2.0)
    highlight = analyzer.build_highlights([quote])[0]
    assert highlight.message == "PETR4 subiu 4.0% no mês."


def test_prioritizes_week_over_day_when_month_not_significant(analyzer: PriceAnalyzer) -> None:
    quote = _quote(change_percent_month=1.0, change_percent_week=-2.5, change_percent_day=1.0)
    highlight = analyzer.build_highlights([quote])[0]
    assert highlight.message == "PETR4 caiu 2.5% na semana."


def test_uses_day_when_month_and_week_not_significant(analyzer: PriceAnalyzer) -> None:
    quote = _quote(change_percent_month=1.0, change_percent_week=1.0, change_percent_day=-1.2)
    highlight = analyzer.build_highlights([quote])[0]
    assert highlight.message == "PETR4 caiu 1.2% no dia."


def test_fii_below_book_value_when_no_significant_price_change(analyzer: PriceAnalyzer) -> None:
    quote = _quote(
        ticker="HGLG11",
        price=150.0,
        book_value=160.0,
        change_percent_month=1.0,
        change_percent_week=1.0,
        change_percent_day=0.5,
    )
    highlight = analyzer.build_highlights([quote])[0]
    assert highlight.message == "HGLG11 negocia abaixo do valor patrimonial."


def test_fii_month_change_takes_priority_over_book_value(analyzer: PriceAnalyzer) -> None:
    quote = _quote(
        ticker="HGLG11",
        price=150.0,
        book_value=160.0,
        change_percent_month=-3.5,
        change_percent_week=1.0,
        change_percent_day=0.5,
    )
    highlight = analyzer.build_highlights([quote])[0]
    assert highlight.message == "HGLG11 caiu 3.5% no mês."


def test_fallback_price_when_no_changes_available(analyzer: PriceAnalyzer) -> None:
    quote = _quote(
        change_percent_day=None,
        change_percent_week=None,
        change_percent_month=None,
        price=28.75,
    )
    highlight = analyzer.build_highlights([quote])[0]
    assert highlight.message == "PETR4 negociado a R$ 28.75."
