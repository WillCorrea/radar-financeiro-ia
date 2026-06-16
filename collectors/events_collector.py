from __future__ import annotations

import csv
import io
import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta

import httpx

from app.config import settings
from collectors.stocks_collector import _extract_error_message, apply_brapi_request_delay

logger = logging.getLogger(__name__)

# Portal Dados Abertos CVM — fatos relevantes (metadados em CSV).
# https://dados.cvm.gov.br/dataset/?tags=fato+relevante
CVM_FACTS_BASE_URL = (
    "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FATO_RELEVANTE/DADOS"
)
BRAPI_QUOTE_URL = "https://brapi.dev/api/quote"


@dataclass
class CorporateEvent:
    ticker: str
    title: str
    published_at: date
    summary: str | None = None
    source_url: str | None = None


class EventsCollector:
    """Coleta fatos relevantes da CVM (CSV) filtrados por ticker monitorado.

    Ticker → CNPJ via brapi.dev. FIIs e ativos sem CNPJ retornam lista vazia.
    """

    def __init__(self, lookback_days: int | None = None) -> None:
        self.lookback_days = lookback_days if lookback_days is not None else settings.events_lookback_days

    def fetch_events(self, tickers: list[str]) -> list[CorporateEvent]:
        if not tickers:
            return []

        try:
            fact_rows = self._load_cvm_facts()
        except httpx.HTTPError as exc:
            logger.warning("CVM fatos relevantes indisponível: %s", exc)
            return []
        except Exception as exc:
            logger.warning("Falha ao processar CSV CVM: %s", exc)
            return []

        if not fact_rows:
            return []

        min_date = date.today() - timedelta(days=self.lookback_days)
        events: list[CorporateEvent] = []

        with httpx.Client(timeout=30.0) as client:
            for index, ticker in enumerate(tickers):
                if index > 0:
                    apply_brapi_request_delay()
                symbol = ticker.strip().upper()
                if not symbol:
                    continue

                cnpj = self._fetch_ticker_cnpj(client, symbol)
                if not cnpj:
                    logger.warning("CNPJ não encontrado para %s — fatos relevantes ignorados", symbol)
                    continue

                events.extend(
                    self._events_for_cnpj(symbol, cnpj, fact_rows, min_date=min_date),
                )

        return events

    def _load_cvm_facts(self) -> list[dict[str, str]]:
        years = _years_for_lookback(self.lookback_days)
        rows: list[dict[str, str]] = []

        with httpx.Client(timeout=60.0) as client:
            for year in years:
                url = f"{CVM_FACTS_BASE_URL}/fato_relevante_cia_aberta_{year}.csv"
                try:
                    response = client.get(url)
                except httpx.HTTPError as exc:
                    logger.warning("CVM download falhou (%s): %s", year, exc)
                    continue

                if response.status_code == 404:
                    continue

                if response.status_code >= 400:
                    logger.warning("CVM retornou %s para ano %s", response.status_code, year)
                    continue

                rows.extend(_parse_cvm_csv(response.content))

        return rows

    def _fetch_ticker_cnpj(self, client: httpx.Client, ticker: str) -> str | None:
        url = f"{BRAPI_QUOTE_URL}/{ticker}"
        headers = self._build_brapi_headers()

        try:
            response = client.get(url, headers=headers)
        except httpx.HTTPError as exc:
            logger.warning("BRAPI CNPJ rede falhou para %s: %s", ticker, exc)
            return None

        if response.status_code >= 400:
            logger.warning(
                "BRAPI CNPJ %s para %s: %s",
                response.status_code,
                ticker,
                _extract_error_message(response),
            )
            return None

        items = response.json().get("results") or []
        if not items:
            return None

        return _extract_cnpj(items[0])

    def _events_for_cnpj(
        self,
        ticker: str,
        cnpj: str,
        fact_rows: list[dict[str, str]],
        *,
        min_date: date,
    ) -> list[CorporateEvent]:
        events: list[CorporateEvent] = []
        seen: set[tuple[str, str, str]] = set()

        for row in fact_rows:
            row_cnpj = _normalize_cnpj(row.get("CNPJ_CIA") or row.get("CNPJ") or "")
            if row_cnpj != cnpj:
                continue

            published_at = _parse_cvm_date(row.get("DT_ENTREGA") or row.get("DT_REFER"))
            if published_at is None or published_at < min_date:
                continue

            title = str(row.get("ASSUNTO") or row.get("TITULO") or "").strip()
            if not title:
                continue

            source_url = str(row.get("LINK_DOC") or row.get("LINK_DOCUMENTO") or "").strip() or None
            dedup_key = (title, published_at.isoformat(), source_url or "")
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            events.append(
                CorporateEvent(
                    ticker=ticker,
                    title=title,
                    published_at=published_at,
                    summary=None,
                    source_url=source_url,
                )
            )

        events.sort(key=lambda event: event.published_at, reverse=True)
        return events

    def _build_brapi_headers(self) -> dict[str, str]:
        if not settings.brapi_token_configured:
            return {}
        return {"Authorization": f"Bearer {settings.brapi_token.strip()}"}


def _years_for_lookback(lookback_days: int) -> list[int]:
    today = date.today()
    years = {today.year}
    if lookback_days > 0:
        years.add((today - timedelta(days=lookback_days)).year)
    return sorted(years)


def _parse_cvm_csv(content: bytes) -> list[dict[str, str]]:
    text = content.decode("latin-1")
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    return [dict(row) for row in reader]


def _extract_cnpj(item: dict) -> str | None:
    direct = item.get("cnpj") or item.get("CNPJ")
    if direct:
        return _normalize_cnpj(str(direct))

    profile = item.get("summaryProfile") or {}
    if isinstance(profile, dict):
        profile_cnpj = profile.get("cnpj") or profile.get("CNPJ")
        if profile_cnpj:
            return _normalize_cnpj(str(profile_cnpj))

    return None


def _normalize_cnpj(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def _parse_cvm_date(value: object) -> date | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text[:10], fmt).date()
        except ValueError:
            continue

    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None
