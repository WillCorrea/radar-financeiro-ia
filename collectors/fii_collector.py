from __future__ import annotations

import logging

import httpx

from app.config import settings
from collectors.stocks_collector import QuoteData, StocksCollector, _calc_period_changes, apply_brapi_request_delay

logger = logging.getLogger(__name__)


class FiiCollector:
    """Coleta cotações de FIIs e enriquece com valor patrimonial (NAV)."""

    FII_HISTORICAL_URL = "https://brapi.dev/api/v2/fii/historical"
    FII_INDICATORS_URL = "https://brapi.dev/api/v2/fii/indicators"

    def __init__(self) -> None:
        self._collector = StocksCollector()

    def fetch_quotes(self, tickers: list[str]) -> list[QuoteData]:
        if tickers and not settings.brapi_token_configured:
            raise ValueError(
                "BRAPI_TOKEN não configurado. FIIs exigem token válido em https://brapi.dev/dashboard"
            )

        quotes = self._collector.fetch_quotes(tickers, include_historical=False)
        if not quotes:
            return quotes

        indicators = self._fetch_indicators(tickers)
        historical = self._fetch_historical_prices(tickers)

        for quote in quotes:
            indicator = indicators.get(quote.ticker, {})
            quote.book_value = indicator.get("nav_per_share")

            hist = historical.get(quote.ticker, [])
            week_change, month_change = _calc_period_changes(hist, quote.price)
            quote.change_percent_week = week_change
            quote.change_percent_month = month_change

            if quote.change_percent_month is None:
                monthly_return = indicator.get("monthly_return")
                if monthly_return is not None:
                    quote.change_percent_month = monthly_return * 100

        return quotes

    def _fetch_indicators(self, tickers: list[str]) -> dict[str, dict[str, float | None]]:
        if not tickers:
            return {}

        headers = self._build_headers()
        indicators: dict[str, dict[str, float | None]] = {}

        with httpx.Client(timeout=30.0) as client:
            for index, ticker in enumerate(tickers):
                if index > 0:
                    apply_brapi_request_delay()

                symbol = ticker.strip().upper()
                if not symbol:
                    continue

                try:
                    response = client.get(
                        self.FII_INDICATORS_URL,
                        params={"symbols": symbol},
                        headers=headers,
                    )
                except httpx.HTTPError as exc:
                    logger.warning("BRAPI indicadores rede falhou para %s: %s", symbol, exc)
                    continue

                if response.status_code >= 400:
                    logger.warning("BRAPI indicadores %s para %s", response.status_code, symbol)
                    continue

                payload = response.json()
                for item in payload.get("fiis", []):
                    item_ticker = str(item.get("symbol", "")).upper()
                    if item_ticker != symbol:
                        continue
                    indicators[item_ticker] = {
                        "nav_per_share": _safe_float(item.get("navPerShare")),
                        "monthly_return": _safe_float(item.get("monthlyReturn")),
                    }

        return indicators

    def _fetch_historical_prices(self, tickers: list[str]) -> dict[str, list[dict]]:
        if not tickers:
            return {}

        headers = self._build_headers()
        historical: dict[str, list[dict]] = {}

        with httpx.Client(timeout=30.0) as client:
            for index, ticker in enumerate(tickers):
                if index > 0:
                    apply_brapi_request_delay()

                symbol = ticker.strip().upper()
                if not symbol:
                    continue

                try:
                    response = client.get(
                        self.FII_HISTORICAL_URL,
                        params={"symbols": symbol, "sortOrder": "asc"},
                        headers=headers,
                    )
                except httpx.HTTPError as exc:
                    logger.warning("BRAPI histórico rede falhou para %s: %s", symbol, exc)
                    continue

                if response.status_code >= 400:
                    logger.warning("BRAPI histórico %s para %s", response.status_code, symbol)
                    continue

                payload = response.json()
                for item in payload.get("fiis", []):
                    item_ticker = str(item.get("symbol", "")).upper()
                    if item_ticker == symbol:
                        historical[item_ticker] = item.get("historicalDataPrice") or []

        return historical

    def _build_headers(self) -> dict[str, str]:
        if not settings.brapi_token_configured:
            return {}
        return {"Authorization": f"Bearer {settings.brapi_token.strip()}"}


def _safe_float(value: object) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None
