from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from collectors.fii_collector import FiiCollector
from collectors.stocks_collector import QuoteData


def _indicators_payload(symbol: str, nav: float) -> dict[str, object]:
    return {
        "fiis": [
            {
                "symbol": symbol,
                "navPerShare": nav,
                "monthlyReturn": 0.02,
            }
        ]
    }


def _historical_payload(symbol: str) -> dict[str, object]:
    return {
        "fiis": [
            {
                "symbol": symbol,
                "historicalDataPrice": [{"close": 100.0}, {"close": 105.0}],
            }
        ]
    }


def _mock_response(payload: dict[str, object], *, status_code: int = 200) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    response.text = ""
    if status_code < 400:
        response.raise_for_status = MagicMock()
    return response


@patch("collectors.fii_collector.settings")
@patch("collectors.fii_collector.apply_brapi_request_delay")
@patch("collectors.fii_collector.httpx.Client")
def test_fetch_quotes_one_request_per_fii_endpoint(
    mock_fii_client_cls: MagicMock,
    mock_delay: MagicMock,
    mock_settings: MagicMock,
) -> None:
    mock_settings.brapi_token_configured = True

    mock_stocks_collector = MagicMock()
    mock_stocks_collector.fetch_quotes.return_value = [
        QuoteData(ticker="HGLG11", price=150.0, change_percent_day=1.0),
        QuoteData(ticker="MXRF11", price=10.0, change_percent_day=0.5),
    ]

    fii_client = MagicMock()
    fii_client.__enter__.return_value = fii_client
    fii_client.get.side_effect = [
        _mock_response(_indicators_payload("HGLG11", 155.0)),
        _mock_response(_indicators_payload("MXRF11", 10.5)),
        _mock_response(_historical_payload("HGLG11")),
        _mock_response(_historical_payload("MXRF11")),
    ]
    mock_fii_client_cls.return_value = fii_client

    collector = FiiCollector()
    collector._collector = mock_stocks_collector
    quotes = collector.fetch_quotes(["HGLG11", "MXRF11"])

    mock_stocks_collector.fetch_quotes.assert_called_once_with(["HGLG11", "MXRF11"], include_historical=False)
    assert fii_client.get.call_count == 4
    assert mock_delay.call_count == 2
    assert len(quotes) == 2
    assert quotes[0].ticker == "HGLG11"
    assert quotes[0].book_value == pytest.approx(155.0)
    assert quotes[1].ticker == "MXRF11"
    assert quotes[1].book_value == pytest.approx(10.5)

    indicator_calls = [
        call.kwargs["params"]["symbols"]
        for call in fii_client.get.call_args_list[:2]
    ]
    assert indicator_calls == ["HGLG11", "MXRF11"]


@patch("collectors.fii_collector.settings")
@patch("collectors.fii_collector.apply_brapi_request_delay")
@patch("collectors.fii_collector.httpx.Client")
def test_fetch_quotes_partial_indicator_failure(
    mock_fii_client_cls: MagicMock,
    _mock_delay: MagicMock,
    mock_settings: MagicMock,
) -> None:
    mock_settings.brapi_token_configured = True

    mock_stocks_collector = MagicMock()
    mock_stocks_collector.fetch_quotes.return_value = [
        QuoteData(ticker="HGLG11", price=150.0, change_percent_day=1.0),
        QuoteData(ticker="MXRF11", price=10.0, change_percent_day=0.5),
    ]

    fii_client = MagicMock()
    fii_client.__enter__.return_value = fii_client
    fii_client.get.side_effect = [
        _mock_response({}, status_code=400),
        _mock_response(_indicators_payload("MXRF11", 10.5)),
        _mock_response(_historical_payload("HGLG11")),
        _mock_response(_historical_payload("MXRF11")),
    ]
    mock_fii_client_cls.return_value = fii_client

    collector = FiiCollector()
    collector._collector = mock_stocks_collector
    quotes = collector.fetch_quotes(["HGLG11", "MXRF11"])

    hglg = next(quote for quote in quotes if quote.ticker == "HGLG11")
    mxrf = next(quote for quote in quotes if quote.ticker == "MXRF11")

    assert hglg.book_value is None
    assert mxrf.book_value == pytest.approx(10.5)
