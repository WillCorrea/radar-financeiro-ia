from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from analyzers.price_analyzer import PriceHighlight
from collectors.stocks_collector import QuoteData
from jobs.daily_radar_job import DailyRadarJob


@pytest.fixture
def job() -> DailyRadarJob:
    return DailyRadarJob(db=MagicMock())


def test_split_tickers(job: DailyRadarJob) -> None:
    stocks, fiis = job._split_tickers(["PETR4", "VALE3", "HGLG11", "MXRF11"])
    assert stocks == ["PETR4", "VALE3"]
    assert fiis == ["HGLG11", "MXRF11"]


def test_build_message_format(job: DailyRadarJob) -> None:
    highlights = [
        PriceHighlight(ticker="PETR4", message="PETR4 caiu 3.2% na semana."),
        PriceHighlight(ticker="HGLG11", message="HGLG11 negocia abaixo do valor patrimonial."),
    ]

    message = job._build_message(highlights, "Mercado com sinais mistos.")

    assert message.startswith("<b>Radar Financeiro - ")
    assert "• PETR4 caiu 3.2% na semana." in message
    assert "• HGLG11 negocia abaixo do valor patrimonial." in message
    assert "<b>Resumo IA:</b>" in message
    assert message.endswith("Mercado com sinais mistos.")


@patch("jobs.daily_radar_job.TelegramSender")
@patch("jobs.daily_radar_job.SummaryAgent")
@patch("jobs.daily_radar_job.FiiCollector")
@patch("jobs.daily_radar_job.StocksCollector")
def test_run_uses_mocks_without_external_calls(
    mock_stocks_cls: MagicMock,
    mock_fii_cls: MagicMock,
    mock_summary_cls: MagicMock,
    mock_telegram_cls: MagicMock,
) -> None:
    mock_stocks = mock_stocks_cls.return_value
    mock_fii = mock_fii_cls.return_value
    mock_summary = mock_summary_cls.return_value
    mock_telegram = mock_telegram_cls.return_value

    mock_stocks.fetch_quotes.return_value = [
        QuoteData(ticker="PETR4", price=30.0, change_percent_month=-4.0),
    ]
    mock_fii.fetch_quotes.return_value = []
    mock_summary.generate_daily_summary.return_value = "Resumo mockado."

    db = MagicMock()
    user = MagicMock()
    user.telegram_chat_id = "123"
    user.assets = []
    db.query.return_value.first.return_value = user
    db.query.return_value.filter.return_value.first.return_value = None

    job = DailyRadarJob(db)
    with patch.object(job, "_resolve_tickers", return_value=["PETR4"]), patch.object(job, "_persist"):
        message = job.run()

    mock_stocks.fetch_quotes.assert_called_once_with(["PETR4"])
    mock_fii.fetch_quotes.assert_called_once_with([])
    mock_summary.generate_daily_summary.assert_called_once()
    mock_telegram.send_message.assert_called_once()
    assert "PETR4" in message
    assert "Resumo mockado." in message
