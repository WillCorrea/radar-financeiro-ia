from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.config import settings
from collectors.dividends_collector import DividendEvent
from collectors.events_collector import CorporateEvent
from database.models import Alert, Asset

# Tipos de alerta do MVP 2 (valores em alerts.alert_type)
ALERT_TYPE_DIVIDEND = "dividend"
ALERT_TYPE_JCP = "jcp"
ALERT_TYPE_CORPORATE = "corporate_event"

EVENT_ALERT_TYPES = frozenset({ALERT_TYPE_DIVIDEND, ALERT_TYPE_JCP, ALERT_TYPE_CORPORATE})


@dataclass
class EventHighlight:
    ticker: str
    alert_type: str
    message: str
    fingerprint: str
    title: str


class EventAnalyzer:
    """Filtra, formata e deduplica eventos corporativos e proventos."""

    def build_highlights(
        self,
        dividends: list[DividendEvent],
        corporate_events: list[CorporateEvent],
        db: Session,
    ) -> list[EventHighlight]:
        min_date = date.today() - timedelta(days=settings.events_lookback_days)
        highlights: list[EventHighlight] = []
        seen_fingerprints: set[str] = set()

        for event in dividends:
            if not _is_dividend_in_lookback(event, min_date):
                continue
            highlight = _dividend_highlight(event)
            if highlight.fingerprint in seen_fingerprints:
                continue
            if _fingerprint_exists(db, highlight.fingerprint):
                continue
            seen_fingerprints.add(highlight.fingerprint)
            highlights.append(highlight)

        for event in corporate_events:
            if event.published_at < min_date:
                continue
            highlight = _corporate_highlight(event)
            if highlight.fingerprint in seen_fingerprints:
                continue
            if _fingerprint_exists(db, highlight.fingerprint):
                continue
            seen_fingerprints.add(highlight.fingerprint)
            highlights.append(highlight)

        return highlights


def _dividend_highlight(event: DividendEvent) -> EventHighlight:
    alert_type = ALERT_TYPE_JCP if event.event_type == "jcp" else ALERT_TYPE_DIVIDEND
    provento = "JCP" if alert_type == ALERT_TYPE_JCP else "dividendos"
    amount = _format_brl(event.amount_per_share)
    ex_date = _format_date(event.ex_date)
    payment_date = _format_date(event.payment_date)

    message = (
        f"{event.ticker} anunciou {provento} de {amount} por ação.\n"
        f"Data-base: {ex_date} | Pagamento: {payment_date}"
    )
    fingerprint = _build_fingerprint(
        event.ticker,
        alert_type,
        event.ex_date,
        event.payment_date,
        f"{event.amount_per_share:.4f}",
    )
    title = f"{'JCP' if alert_type == ALERT_TYPE_JCP else 'Dividendo'} {event.ticker}"
    return EventHighlight(
        ticker=event.ticker,
        alert_type=alert_type,
        message=message,
        fingerprint=fingerprint,
        title=title,
    )


def _corporate_highlight(event: CorporateEvent) -> EventHighlight:
    published = _format_date(event.published_at)
    message = f"{event.ticker} — fato relevante: {event.title}\nPublicado em: {published}"
    if event.source_url:
        message = f"{message}\nDocumento: {event.source_url}"

    fingerprint = _build_fingerprint(
        event.ticker,
        ALERT_TYPE_CORPORATE,
        event.published_at,
        None,
        _hash_text(event.title),
    )
    return EventHighlight(
        ticker=event.ticker,
        alert_type=ALERT_TYPE_CORPORATE,
        message=message,
        fingerprint=fingerprint,
        title=f"Fato relevante {event.ticker}",
    )


def _fingerprint_exists(db: Session, fingerprint: str) -> bool:
    if db.query(Alert).filter(Alert.fingerprint == fingerprint).first():
        return True

    return _legacy_alert_exists(db, fingerprint)


def _legacy_alert_exists(db: Session, fingerprint: str) -> bool:
    """Compatibilidade antes da coluna fingerprint — dedup por ticker/tipo/data."""
    parts = fingerprint.split("|")
    if len(parts) < 5:
        return False

    ticker, alert_type, ref_date, _, extra = parts[0], parts[1], parts[2], parts[3], parts[4]
    asset = db.query(Asset).filter(Asset.ticker == ticker).first()
    if not asset:
        return False

    query = db.query(Alert).filter(
        Alert.asset_id == asset.id,
        Alert.alert_type == alert_type,
    )
    for alert in query.all():
        if ref_date in alert.content and (extra in alert.content or alert_type == ALERT_TYPE_CORPORATE):
            return True
    return False


def _is_dividend_in_lookback(event: DividendEvent, min_date: date) -> bool:
    reference = event.ex_date or event.payment_date
    if reference is None:
        return True
    return reference >= min_date


def _build_fingerprint(
    ticker: str,
    alert_type: str,
    ref_date: date | None,
    payment_date: date | None,
    extra: str,
) -> str:
    ref = ref_date.isoformat() if ref_date else "-"
    pay = payment_date.isoformat() if payment_date else "-"
    return f"{ticker}|{alert_type}|{ref}|{pay}|{extra}"


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _format_brl(value: float) -> str:
    formatted = f"{value:,.2f}"
    return "R$ " + formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def _format_date(value: date | None) -> str:
    if value is None:
        return "—"
    return value.strftime("%d/%m/%Y")
