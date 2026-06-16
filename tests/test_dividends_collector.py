from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import httpx
import pytest

from collectors.dividends_collector import DividendsCollector


def _dividends_payload(
    *,
    symbol: str = "PETR4",
    cash_dividends: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return {
        "results": [
            {
                "symbol": symbol,
                "dividendsData": {
                    "cashDividends": cash_dividends
                    or [
                        {
                            "type": "DIVIDENDO",
                            "rate": 1.25,
                            "lastDatePrior": "2026-08-15",
                            "paymentDate": "2026-08-30",
                        },
                        {
                            "type": "JCP",
                            "rate": 0.8,
                            "lastDatePrior": "2026-06-10",
                            "paymentDate": "2026-06-25",
                        },
                    ],
                },
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


@patch("collectors.dividends_collector.apply_brapi_request_delay")
@patch("collectors.dividends_collector.httpx.Client")
def test_fetch_events_parses_dividend_and_jcp(mock_client_cls: MagicMock, _mock_delay: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.get.return_value = _mock_response(_dividends_payload())
    mock_client_cls.return_value = mock_client

    collector = DividendsCollector()
    events = collector.fetch_events(["PETR4"])

    assert len(events) == 2
    dividend = events[0]
    assert dividend.ticker == "PETR4"
    assert dividend.event_type == "dividend"
    assert dividend.amount_per_share == 1.25
    assert dividend.ex_date == date(2026, 8, 15)
    assert dividend.payment_date == date(2026, 8, 30)
    assert dividend.label == "DIVIDENDO"

    jcp = events[1]
    assert jcp.event_type == "jcp"
    assert jcp.amount_per_share == 0.8


@patch("collectors.dividends_collector.apply_brapi_request_delay")
@patch("collectors.dividends_collector.httpx.Client")
def test_fetch_events_one_request_per_ticker(mock_client_cls: MagicMock, mock_delay: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.get.side_effect = [
        _mock_response(_dividends_payload(symbol="PETR4", cash_dividends=[{"type": "DIVIDENDO", "rate": 1.0}])),
        _mock_response(_dividends_payload(symbol="VALE3", cash_dividends=[{"type": "JCP", "rate": 0.5}])),
    ]
    mock_client_cls.return_value = mock_client

    collector = DividendsCollector()
    events = collector.fetch_events(["PETR4", "VALE3"])

    assert mock_client.get.call_count == 2
    mock_delay.assert_called_once()
    assert len(events) == 2
    assert events[0].ticker == "PETR4"
    assert events[1].ticker == "VALE3"

    urls = [call.args[0] for call in mock_client.get.call_args_list]
    assert urls == [
        "https://brapi.dev/api/quote/PETR4",
        "https://brapi.dev/api/quote/VALE3",
    ]
    params = [call.kwargs["params"] for call in mock_client.get.call_args_list]
    assert params == [{"dividends": "true"}, {"dividends": "true"}]


@patch("collectors.dividends_collector.apply_brapi_request_delay")
@patch("collectors.dividends_collector.httpx.Client")
def test_fetch_events_partial_failure_continues(mock_client_cls: MagicMock, _mock_delay: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.get.side_effect = [
        _mock_response({"results": []}, status_code=400),
        _mock_response(_dividends_payload(symbol="VALE3", cash_dividends=[{"type": "DIVIDENDO", "rate": 2.0}])),
    ]
    mock_client_cls.return_value = mock_client

    collector = DividendsCollector()
    events = collector.fetch_events(["PETR4", "VALE3"])

    assert len(events) == 1
    assert events[0].ticker == "VALE3"


@patch("collectors.dividends_collector.httpx.Client")
def test_fetch_events_returns_empty_for_no_tickers(mock_client_cls: MagicMock) -> None:
    collector = DividendsCollector()
    assert collector.fetch_events([]) == []
    mock_client_cls.assert_not_called()


@patch("collectors.dividends_collector.apply_brapi_request_delay")
@patch("collectors.dividends_collector.httpx.Client")
def test_fetch_events_empty_when_no_cash_dividends(mock_client_cls: MagicMock, _mock_delay: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.get.return_value = _mock_response(
        {"results": [{"symbol": "HGLG11", "dividendsData": {"cashDividends": []}}]}
    )
    mock_client_cls.return_value = mock_client

    collector = DividendsCollector()
    events = collector.fetch_events(["HGLG11"])

    assert events == []


@patch("collectors.dividends_collector.settings")
@patch("collectors.dividends_collector.httpx.Client")
def test_fetch_events_raises_on_401(mock_client_cls: MagicMock, mock_settings: MagicMock) -> None:
    mock_settings.brapi_token_configured = False
    mock_settings.brapi_token = ""

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.get.return_value = _mock_response({}, status_code=401)
    mock_client_cls.return_value = mock_client

    collector = DividendsCollector()
    with pytest.raises(ValueError, match="401"):
        collector.fetch_events(["PETR4"])
