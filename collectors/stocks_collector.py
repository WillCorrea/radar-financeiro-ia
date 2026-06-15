from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class QuoteData:
    ticker: str
    price: float
    change_percent_day: float | None = None
    change_percent_week: float | None = None
    change_percent_month: float | None = None
    book_value: float | None = None
    name: str | None = None


def apply_brapi_request_delay() -> None:
    delay = settings.brapi_request_delay_seconds
    if delay > 0:
        time.sleep(delay)


class StocksCollector:
    """Coleta cotações de ações via brapi.dev (gratuita)."""

    BASE_URL = "https://brapi.dev/api"
    HISTORICAL_PARAMS = {"range": "1mo", "interval": "1d"}
    WEEK_SESSIONS_BACK = 5

    def fetch_quotes(self, tickers: list[str], *, include_historical: bool = True) -> list[QuoteData]:
        if not tickers:
            return []

        results: list[QuoteData] = []
        with httpx.Client(timeout=30.0) as client:
            for index, ticker in enumerate(tickers):
                if index > 0:
                    apply_brapi_request_delay()
                quote = self._fetch_single_quote(client, ticker, include_historical=include_historical)
                if quote is not None:
                    results.append(quote)

        return results

    def _fetch_single_quote(
        self,
        client: httpx.Client,
        ticker: str,
        *,
        include_historical: bool,
    ) -> QuoteData | None:
        symbol = ticker.strip().upper()
        if not symbol:
            return None

        url = f"{self.BASE_URL}/quote/{symbol}"
        headers = self._build_headers()
        params = dict(self.HISTORICAL_PARAMS) if include_historical else None

        try:
            response = client.get(url, params=params, headers=headers)
        except httpx.HTTPError as exc:
            logger.warning("BRAPI rede falhou para %s: %s", symbol, exc)
            return None

        if response.status_code == 401:
            self._raise_for_status(response)

        if response.status_code >= 400:
            logger.warning(
                "BRAPI %s para %s: %s",
                response.status_code,
                symbol,
                _extract_error_message(response),
            )
            return None

        payload = response.json()
        items = payload.get("results") or []
        if not items:
            logger.warning("BRAPI sem dados para %s", symbol)
            return None

        return self._parse_quote_item(items[0])

    def _parse_quote_item(self, item: dict) -> QuoteData | None:
        price = float(item.get("regularMarketPrice") or 0)
        if price <= 0:
            ticker = str(item.get("symbol", "")).upper()
            logger.warning("BRAPI preço inválido para %s", ticker)
            return None

        change_percent_week, change_percent_month = _calc_period_changes(
            item.get("historicalDataPrice") or [],
            price,
        )
        return QuoteData(
            ticker=str(item.get("symbol", "")).upper(),
            name=item.get("shortName") or item.get("longName"),
            price=price,
            change_percent_day=_safe_float(item.get("regularMarketChangePercent")),
            change_percent_week=change_percent_week,
            change_percent_month=change_percent_month,
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
                        "FIIs e histórico exigem token válido em https://brapi.dev/dashboard"
                    ) from exc
                raise ValueError(
                    "BRAPI retornou 401: token inválido ou expirado. "
                    "Atualize BRAPI_TOKEN em https://brapi.dev/dashboard"
                ) from exc
            if response.status_code == 400:
                detail = _extract_error_message(response)
                raise ValueError(
                    f"BRAPI retornou 400: {detail}. "
                    "FIIs não aceitam range/interval no /api/quote; use o collector de FIIs."
                ) from exc
            raise


def _extract_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text[:200] or "requisição inválida"
    return str(payload.get("message") or payload.get("error") or "requisição inválida")


def _calc_period_changes(
    historical: list[dict],
    current_price: float,
) -> tuple[float | None, float | None]:
    if current_price <= 0 or not historical:
        return None, None

    closes = [_historical_close(entry) for entry in historical]
    closes = [close for close in closes if close is not None and close > 0]
    if not closes:
        return None, None

    week_change = None
    if len(closes) > StocksCollector.WEEK_SESSIONS_BACK:
        week_change = _percent_change(current_price, closes[-(StocksCollector.WEEK_SESSIONS_BACK + 1)])

    month_change = None
    if len(closes) >= 2:
        month_change = _percent_change(current_price, closes[0])

    return week_change, month_change


def _historical_close(entry: dict) -> float | None:
    return _safe_float(entry.get("adjustedClose")) or _safe_float(entry.get("close"))


def _percent_change(current_price: float, reference_price: float | None) -> float | None:
    if reference_price is None or reference_price <= 0:
        return None
    return ((current_price - reference_price) / reference_price) * 100


def _safe_float(value: object) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None
