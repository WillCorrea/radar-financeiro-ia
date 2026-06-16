from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from typing import Literal

import httpx

from app.config import settings
from collectors.stocks_collector import _extract_error_message, apply_brapi_request_delay

logger = logging.getLogger(__name__)

DividendEventType = Literal["dividend", "jcp"]


@dataclass
class DividendEvent:
    ticker: str
    event_type: DividendEventType
    amount_per_share: float
    ex_date: date | None = None
    payment_date: date | None = None
    label: str | None = None


class DividendsCollector:
    """Coleta proventos em dinheiro (dividendos e JCP) via brapi.dev.

    FIIs: usa o mesmo endpoint /api/quote/{ticker}?dividends=true. Quando a BRAPI
    não retorna cashDividends (comum em alguns fundos), retorna lista vazia.
    """

    BASE_URL = "https://brapi.dev/api"
    DIVIDENDS_PARAMS = {"dividends": "true"}

    def fetch_events(self, tickers: list[str]) -> list[DividendEvent]:
        if not tickers:
            return []

        events: list[DividendEvent] = []
        with httpx.Client(timeout=30.0) as client:
            for index, ticker in enumerate(tickers):
                if index > 0:
                    apply_brapi_request_delay()
                events.extend(self._fetch_ticker_events(client, ticker))

        return events

    def _fetch_ticker_events(self, client: httpx.Client, ticker: str) -> list[DividendEvent]:
        symbol = ticker.strip().upper()
        if not symbol:
            return []

        url = f"{self.BASE_URL}/quote/{symbol}"
        headers = self._build_headers()

        try:
            response = client.get(url, params=self.DIVIDENDS_PARAMS, headers=headers)
        except httpx.HTTPError as exc:
            logger.warning("BRAPI dividendos rede falhou para %s: %s", symbol, exc)
            return []

        if response.status_code == 401:
            self._raise_for_status(response)

        if response.status_code >= 400:
            logger.warning(
                "BRAPI dividendos %s para %s: %s",
                response.status_code,
                symbol,
                _extract_error_message(response),
            )
            return []

        payload = response.json()
        items = payload.get("results") or []
        if not items:
            logger.warning("BRAPI dividendos sem dados para %s", symbol)
            return []

        return self._parse_cash_dividends(symbol, items[0])

    def _parse_cash_dividends(self, ticker: str, item: dict) -> list[DividendEvent]:
        dividends_data = item.get("dividendsData") or {}
        cash_dividends = dividends_data.get("cashDividends") or []
        if not cash_dividends:
            return []

        events: list[DividendEvent] = []
        for entry in cash_dividends:
            event = self._parse_cash_dividend_entry(ticker, entry)
            if event is not None:
                events.append(event)

        return events

    def _parse_cash_dividend_entry(self, ticker: str, entry: dict) -> DividendEvent | None:
        raw_type = str(entry.get("type") or entry.get("label") or "").strip()
        event_type = _map_event_type(raw_type)
        if event_type is None:
            return None

        amount = _safe_float(entry.get("rate")) or _safe_float(entry.get("amount"))
        if amount is None or amount <= 0:
            return None

        return DividendEvent(
            ticker=ticker,
            event_type=event_type,
            amount_per_share=amount,
            ex_date=_parse_date(entry.get("lastDatePrior") or entry.get("exDate")),
            payment_date=_parse_date(entry.get("paymentDate")),
            label=raw_type or None,
        )

    def _build_headers(self) -> dict[str, str]:
        if not settings.brapi_token_configured:
            return {}
        return {"Authorization": f"Bearer {settings.brapi_token.strip()}"}

    def _raise_for_status(self, response: httpx.Response) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if response.status_code == 401:
                if not settings.brapi_token_configured:
                    raise ValueError(
                        "BRAPI retornou 401: configure BRAPI_TOKEN no .env. "
                        "Dividendos exigem token válido em https://brapi.dev/dashboard"
                    ) from exc
                raise ValueError(
                    "BRAPI retornou 401: token inválido ou expirado. "
                    "Atualize BRAPI_TOKEN em https://brapi.dev/dashboard"
                ) from exc
            raise


def _map_event_type(raw_type: str) -> DividendEventType | None:
    normalized = raw_type.upper()
    if normalized in {"DIVIDENDO", "RENDIMENTO", "AMORTIZACAO", "AMORTIZAÇÃO"}:
        return "dividend"
    if normalized == "JCP":
        return "jcp"
    return None


def _parse_date(value: object) -> date | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _safe_float(value: object) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None
