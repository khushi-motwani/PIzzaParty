import yfinance as yf
import requests
import logging
from math import isnan
from dto.quote_dto import QuoteDTO
from exception.finance_exceptions import TickerNotFoundError, FinanceApiError

logger = logging.getLogger(__name__)

CACHED_API_URL = "https://c4rm9elh30.execute-api.us-east-1.amazonaws.com/default/cachedPriceData"

MOCK_DATA = {
    "AAPL": {"price": 195.5, "previous_close": 194.8, "market_cap": 2800000000000, "day_high": 198.2, "day_low": 194.9},
    "TSLA": {"price": 197.5, "previous_close": 196.2, "market_cap": 625000000000, "day_high": 200.1, "day_low": 195.3},
    "AMZN": {"price": 175.3, "previous_close": 174.5, "market_cap": 1800000000000, "day_high": 178.5, "day_low": 173.1},
    "MSFT": {"price": 445.2, "previous_close": 443.1, "market_cap": 3300000000000, "day_high": 450.0, "day_low": 442.1},
    "GOOGL": {"price": 142.8, "previous_close": 141.5, "market_cap": 1900000000000, "day_high": 145.2, "day_low": 140.5},
    "FB": {"price": 320.5, "previous_close": 318.2, "market_cap": 800000000000, "day_high": 325.0, "day_low": 318.2},
    "C": {"price": 52.3, "previous_close": 51.8, "market_cap": 170000000000, "day_high": 53.1, "day_low": 51.5},
}


class FinanceClient:
    def __init__(self, ticker_factory=None, http_client=None):
        self.ticker_factory = ticker_factory or yf.Ticker
        self.http_client = http_client or requests

    def get_quote(self, ticker):
        try:
            return self._get_from_yfinance(ticker)
        except (TickerNotFoundError, FinanceApiError):
            logger.info(f"yfinance failed for {ticker}, trying cached API...")
            try:
                return self._get_from_cached_api(ticker)
            except (TickerNotFoundError, FinanceApiError):
                logger.info(f"Cached API failed for {ticker}, using mock data...")
                return self._get_from_mock_data(ticker)

    def _get_from_yfinance(self, ticker):
        try:
            ticker_obj = self.ticker_factory(ticker)

            if ticker_obj is None:
                raise TickerNotFoundError(ticker)

            hist = ticker_obj.history(period="5d")

            if hist is None or hist.empty:
                raise TickerNotFoundError(ticker)

            latest = hist.iloc[-1]
            close_price = float(latest["Close"])
            previous_close = float(hist.iloc[-2]["Close"]) if len(hist) > 1 else None

            logger.info(f"Retrieved data for {ticker} from yfinance")
            return QuoteDTO(
                ticker=ticker,
                price=close_price,
                currency="USD",
                previous_close=previous_close,
                market_cap=None,
                day_high=float(latest["High"]),
                day_low=float(latest["Low"])
            )
        except TickerNotFoundError:
            raise
        except Exception as e:
            raise FinanceApiError(ticker, "yfinance")

    def _get_from_cached_api(self, ticker):
        try:
            response = self.http_client.get(
                CACHED_API_URL,
                params={"ticker": ticker},
                timeout=5
            )
            response.raise_for_status()
            data = response.json()

            if not data or "price_data" not in data or "close" not in data["price_data"]:
                raise TickerNotFoundError(ticker)

            prices = data["price_data"]["close"]
            if not prices or len(prices) == 0:
                raise TickerNotFoundError(ticker)

            latest_price = float(prices[-1])

            # Handle NaN values and convert to None
            if isnan(latest_price):
                raise TickerNotFoundError(ticker)

            # Calculate day high and low from available prices, use last 5 or all if less
            recent_prices = prices[-5:] if len(prices) >= 5 else prices
            day_high = max(float(p) for p in recent_prices if not isnan(float(p)))
            day_low = min(float(p) for p in recent_prices if not isnan(float(p)))
            previous_close = float(prices[-2]) if len(prices) > 1 and not isnan(float(prices[-2])) else None

            logger.info(f"Retrieved data for {ticker} from cached API")
            return QuoteDTO(
                ticker=ticker,
                price=latest_price,
                currency="USD",
                previous_close=previous_close,
                market_cap=None,
                day_high=day_high,
                day_low=day_low
            )
        except TickerNotFoundError:
            raise
        except Exception:
            raise FinanceApiError(ticker, "cached-api")

    def _get_from_mock_data(self, ticker):
        if ticker.upper() not in MOCK_DATA:
            raise TickerNotFoundError(ticker)

        data = MOCK_DATA[ticker.upper()]
        logger.warning(f"Using mock data for {ticker} (real API unavailable)")

        return QuoteDTO(
            ticker=ticker,
            price=data["price"],
            currency="USD",
            previous_close=data.get("previous_close"),
            market_cap=data.get("market_cap"),
            day_high=data["day_high"],
            day_low=data["day_low"]
        )
