from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from collectors.stocks_collector import StocksCollector


def _historical_closes(base: float, count: int) -> list[dict[str, float]]:
    return [{"close": base + index} for index in range(count)]


def _brapi_payload(
    *,
    symbol: str = "PETR4",
    price: float = 110.0,
    day_change: float = -1.5,
    historical: list[dict[str, float]] | None = None,
) -> dict[str, object]:
    return {
        "results": [
            {
                "symbol": symbol,
                "shortName": "PETROBRAS",
                "regularMarketPrice": price,
                "regularMarketChangePercent": day_change,
                "historicalDataPrice": historical or _historical_closes(100.0, 7),
            }
        ]
    }


def _mock_response(payload: dict[str, object], *, status_code: int = 200) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    response.text = ""
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error",
            request=MagicMock(),
            response=response,
        )
    else:
        response.raise_for_status = MagicMock()
    return response


@patch("collectors.stocks_collector.apply_brapi_request_delay")
@patch("collectors.stocks_collector.httpx.Client")
def test_fetch_quotes_parses_quote_data(mock_client_cls: MagicMock, _mock_delay: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.get.return_value = _mock_response(_brapi_payload())
    mock_client_cls.return_value = mock_client

    collector = StocksCollector()
    quotes = collector.fetch_quotes(["PETR4"])

    assert len(quotes) == 1
    quote = quotes[0]
    assert quote.ticker == "PETR4"
    assert quote.name == "PETROBRAS"
    assert quote.price == 110.0
    assert quote.change_percent_day == -1.5
    assert quote.change_percent_month == pytest.approx(10.0)
    assert quote.change_percent_week == pytest.approx(8.910891)


@patch("collectors.stocks_collector.httpx.Client")
def test_fetch_quotes_returns_empty_for_no_tickers(mock_client_cls: MagicMock) -> None:
    collector = StocksCollector()
    quotes = collector.fetch_quotes([])
    assert quotes == []
    mock_client_cls.assert_not_called()


@patch("collectors.stocks_collector.apply_brapi_request_delay")
@patch("collectors.stocks_collector.httpx.Client")
def test_fetch_quotes_without_historical_skips_range_params(
    mock_client_cls: MagicMock,
    _mock_delay: MagicMock,
) -> None:
    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.get.return_value = _mock_response(
        {
            "results": [
                {
                    "symbol": "HGLG11",
                    "regularMarketPrice": 150.0,
                    "regularMarketChangePercent": 0.8,
                }
            ]
        }
    )
    mock_client_cls.return_value = mock_client

    collector = StocksCollector()
    quotes = collector.fetch_quotes(["HGLG11"], include_historical=False)

    _, kwargs = mock_client.get.call_args
    assert kwargs["params"] is None
    assert quotes[0].ticker == "HGLG11"
    assert quotes[0].change_percent_week is None
    assert quotes[0].change_percent_month is None


@patch("collectors.stocks_collector.apply_brapi_request_delay")
@patch("collectors.stocks_collector.httpx.Client")
def test_fetch_quotes_one_request_per_ticker(mock_client_cls: MagicMock, mock_delay: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.get.side_effect = [
        _mock_response(_brapi_payload(symbol="PETR4", price=110.0)),
        _mock_response(_brapi_payload(symbol="VALE3", price=62.0, day_change=2.0)),
    ]
    mock_client_cls.return_value = mock_client

    collector = StocksCollector()
    quotes = collector.fetch_quotes(["PETR4", "VALE3"])

    assert mock_client.get.call_count == 2
    mock_delay.assert_called_once()
    assert [quote.ticker for quote in quotes] == ["PETR4", "VALE3"]
    urls = [call.args[0] for call in mock_client.get.call_args_list]
    assert urls == [
        "https://brapi.dev/api/quote/PETR4",
        "https://brapi.dev/api/quote/VALE3",
    ]


@patch("collectors.stocks_collector.apply_brapi_request_delay")
@patch("collectors.stocks_collector.httpx.Client")
def test_fetch_quotes_partial_failure_continues(mock_client_cls: MagicMock, mock_delay: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.get.side_effect = [
        _mock_response({"results": []}, status_code=400),
        _mock_response(_brapi_payload(symbol="VALE3", price=62.0, day_change=2.0)),
    ]
    mock_client_cls.return_value = mock_client

    collector = StocksCollector()
    quotes = collector.fetch_quotes(["PETR4", "VALE3"])

    assert mock_client.get.call_count == 2
    assert len(quotes) == 1
    assert quotes[0].ticker == "VALE3"
