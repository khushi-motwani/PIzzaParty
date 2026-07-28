import yfinance as yf
from dto.quote_dto import QuoteDTO
from exception.finance_exceptions import TickerNotFoundError, FinanceApiError


class FinanceClient:
    def __init__(self, ticker_factory=None):
        self.ticker_factory = ticker_factory or yf.Ticker

    def get_quote(self, ticker):
        try:
            ticker_obj = self.ticker_factory(ticker)

            if ticker_obj is None:
                raise TickerNotFoundError(f"Ticker '{ticker}' not found or has no price data")

            info = ticker_obj.fast_info

            if info is None or info.get("lastPrice") is None:
                raise TickerNotFoundError(f"Ticker '{ticker}' not found or has no price data")

            return QuoteDTO(
                ticker=ticker,
                price=info.get("lastPrice"),
                currency=info.get("currency", "USD"),
                previous_close=info.get("previousClose"),
                market_cap=info.get("marketCap"),
                day_high=info.get("dayHigh"),
                day_low=info.get("dayLow")
            )
        except TickerNotFoundError:
            raise
        except Exception as e:
            raise FinanceApiError(f"Failed to fetch quote for ticker '{ticker}': {str(e)}")
