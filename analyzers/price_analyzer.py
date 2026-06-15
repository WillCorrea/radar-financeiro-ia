from __future__ import annotations

from dataclasses import dataclass

from collectors.stocks_collector import QuoteData


@dataclass
class PriceHighlight:
    ticker: str
    message: str


class PriceAnalyzer:
    MONTH_THRESHOLD = 3.0
    WEEK_THRESHOLD = 2.0

    def build_highlights(self, quotes: list[QuoteData]) -> list[PriceHighlight]:
        return [self._build_highlight(quote) for quote in quotes]

    def _build_highlight(self, quote: QuoteData) -> PriceHighlight:
        message = self._select_message(quote)
        return PriceHighlight(ticker=quote.ticker, message=message)

    def _select_message(self, quote: QuoteData) -> str:
        if self._is_significant(quote.change_percent_month, self.MONTH_THRESHOLD):
            return self._format_change(quote.ticker, quote.change_percent_month, "no mês")

        if self._is_significant(quote.change_percent_week, self.WEEK_THRESHOLD):
            return self._format_change(quote.ticker, quote.change_percent_week, "na semana")

        if self._is_fii(quote.ticker) and self._is_below_book_value(quote):
            return f"{quote.ticker} negocia abaixo do valor patrimonial."

        if quote.change_percent_day is not None:
            return self._format_change(quote.ticker, quote.change_percent_day, "no dia")

        return f"{quote.ticker} negociado a R$ {quote.price:.2f}."

    def _is_significant(self, change_percent: float | None, threshold: float) -> bool:
        return change_percent is not None and abs(change_percent) >= threshold

    def _is_fii(self, ticker: str) -> bool:
        return ticker.endswith("11")

    def _is_below_book_value(self, quote: QuoteData) -> bool:
        return quote.book_value is not None and quote.price < quote.book_value

    def _format_change(self, ticker: str, change_percent: float, period: str) -> str:
        direction = "subiu" if change_percent >= 0 else "caiu"
        return f"{ticker} {direction} {abs(change_percent):.1f}% {period}."
