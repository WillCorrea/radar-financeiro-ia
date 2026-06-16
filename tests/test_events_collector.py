from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import httpx

from collectors.events_collector import EventsCollector


def _cvm_csv(*rows: dict[str, str]) -> bytes:
    header = "CNPJ_CIA;DENOM_CIA;DT_REFER;DT_ENTREGA;ASSUNTO;LINK_DOC;PROTOCOLO;VERSAO"
    lines = [header]
    for row in rows:
        lines.append(
            ";".join(
                [
                    row.get("CNPJ_CIA", ""),
                    row.get("DENOM_CIA", "CIA"),
                    row.get("DT_REFER", "2026-06-01"),
                    row.get("DT_ENTREGA", row.get("DT_REFER", "2026-06-01")),
                    row.get("ASSUNTO", "Fato relevante"),
                    row.get("LINK_DOC", "https://cvm.example/doc.pdf"),
                    row.get("PROTOCOLO", "1"),
                    row.get("VERSAO", "1"),
                ]
            )
        )
    return "\n".join(lines).encode("latin-1")


def _brapi_quote(cnpj: str) -> dict[str, object]:
    return {"results": [{"symbol": "PETR4", "cnpj": cnpj}]}


def _mock_response(*, content: bytes | None = None, json_payload: dict | None = None, status_code: int = 200) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.content = content or b""
    if json_payload is not None:
        response.json.return_value = json_payload
    response.text = ""
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error",
            request=MagicMock(),
            response=response,
        )
    return response


@patch("collectors.events_collector.date")
@patch("collectors.events_collector.apply_brapi_request_delay")
@patch("collectors.events_collector.httpx.Client")
def test_fetch_events_filters_by_cnpj_and_lookback(
    mock_client_cls: MagicMock,
    _mock_delay: MagicMock,
    mock_date: MagicMock,
) -> None:
    mock_date.today.return_value = date(2026, 6, 15)

    cvm_client = MagicMock()
    brapi_client = MagicMock()
    mock_client_cls.side_effect = [cvm_client, brapi_client]

    cvm_client.__enter__.return_value = cvm_client
    cvm_client.get.return_value = _mock_response(
        content=_cvm_csv(
            {
                "CNPJ_CIA": "33.000.167/0001-01",
                "DT_ENTREGA": "2026-06-10",
                "ASSUNTO": "Aquisição de participação societária",
                "LINK_DOC": "https://cvm.example/a.pdf",
            },
            {
                "CNPJ_CIA": "33.000.167/0001-01",
                "DT_ENTREGA": "2026-01-01",
                "ASSUNTO": "Evento antigo",
            },
            {
                "CNPJ_CIA": "99.999.999/0001-99",
                "DT_ENTREGA": "2026-06-11",
                "ASSUNTO": "Outra empresa",
            },
        )
    )

    brapi_client.__enter__.return_value = brapi_client
    brapi_client.get.return_value = _mock_response(json_payload=_brapi_quote("33000167000101"))

    collector = EventsCollector(lookback_days=30)
    events = collector.fetch_events(["PETR4"])

    assert len(events) == 1
    assert events[0].ticker == "PETR4"
    assert events[0].title == "Aquisição de participação societária"
    assert events[0].published_at == date(2026, 6, 10)
    assert events[0].source_url == "https://cvm.example/a.pdf"


@patch("collectors.events_collector.apply_brapi_request_delay")
@patch("collectors.events_collector.httpx.Client")
def test_fetch_events_returns_empty_when_cvm_fails(
    mock_client_cls: MagicMock,
    _mock_delay: MagicMock,
) -> None:
    cvm_client = MagicMock()
    brapi_client = MagicMock()
    mock_client_cls.side_effect = [cvm_client, brapi_client]

    cvm_client.__enter__.return_value = cvm_client
    cvm_client.get.side_effect = httpx.HTTPError("offline")

    collector = EventsCollector()
    assert collector.fetch_events(["PETR4"]) == []


@patch("collectors.events_collector.date")
@patch("collectors.events_collector.apply_brapi_request_delay")
@patch("collectors.events_collector.httpx.Client")
def test_fetch_events_partial_when_cnpj_missing(
    mock_client_cls: MagicMock,
    _mock_delay: MagicMock,
    mock_date: MagicMock,
) -> None:
    mock_date.today.return_value = date(2026, 6, 15)

    cvm_client = MagicMock()
    brapi_client = MagicMock()
    mock_client_cls.side_effect = [cvm_client, brapi_client]

    cvm_client.__enter__.return_value = cvm_client
    cvm_client.get.return_value = _mock_response(
        content=_cvm_csv(
            {
                "CNPJ_CIA": "33.000.167/0001-01",
                "DT_ENTREGA": "2026-06-10",
                "ASSUNTO": "Fato PETR4",
            }
        )
    )

    brapi_client.__enter__.return_value = brapi_client
    brapi_client.get.side_effect = [
        _mock_response(json_payload={"results": [{"symbol": "PETR4", "cnpj": "33000167000101"}]}),
        _mock_response(json_payload={"results": [{"symbol": "VALE3"}]}),
    ]

    collector = EventsCollector(lookback_days=30)
    events = collector.fetch_events(["PETR4", "VALE3"])

    assert len(events) == 1
    assert events[0].ticker == "PETR4"
    assert brapi_client.get.call_count == 2


@patch("collectors.events_collector.httpx.Client")
def test_fetch_events_empty_for_no_tickers(mock_client_cls: MagicMock) -> None:
    collector = EventsCollector()
    assert collector.fetch_events([]) == []
    mock_client_cls.assert_not_called()
