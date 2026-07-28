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

            # Use history() for a single day to get price data, safer than fast_info
            hist = ticker_obj.history(period="1d")

            if hist is None or hist.empty:
                raise TickerNotFoundError(f"Ticker '{ticker}' not found or has no price data")

            latest = hist.iloc[-1]
            close_price = float(latest["Close"])

            return QuoteDTO(
                ticker=ticker,
                price=close_price,
                currency="USD",
                previous_close=None,
                market_cap=None,
                day_high=float(latest["High"]),
                day_low=float(latest["Low"])
            )
        except TickerNotFoundError:
            raise
        except Exception as e:
            raise FinanceApiError(f"Failed to fetch quote for ticker '{ticker}': {str(e)}")
