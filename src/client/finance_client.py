import os
import requests
import logging
from dto.quote_dto import QuoteDTO
from exception.finance_exceptions import TickerNotFoundError, FinanceApiError

logger = logging.getLogger(__name__)


class FinanceClient:
    def __init__(self, http_client=None, base_url=None):
        self.http_client = http_client or requests
        self.base_url = base_url or os.environ.get("FINANCE_API_BASE_URL", "http://localhost:4000")

    def get_quote(self, ticker):
        return self._get_from_finance_api(ticker)

    def get_history(self, ticker, start=None, end=None):
        return self._get_history_from_finance_api(ticker, start, end)

    def _get_from_finance_api(self, ticker):
        try:
            url = f"{self.base_url}/quote"
            response = self.http_client.get(
                url,
                params={"ticker": ticker.upper()},
                timeout=5
            )

            if response.status_code == 404:
                raise TickerNotFoundError(ticker)

            response.raise_for_status()
            data = response.json()

            logger.info(f"Retrieved data for {ticker} from yahoo-finance-emulator")
            return QuoteDTO(
                ticker=ticker,
                price=data["price"],
                currency=data.get("currency", "USD"),
                previous_close=data.get("previousClose"),
                market_cap=None,
                day_high=data.get("dayHigh"),
                day_low=data.get("dayLow")
            )
        except TickerNotFoundError:
            raise
        except Exception as e:
            raise FinanceApiError(ticker, "yahoo-finance-emulator")

    def _get_history_from_finance_api(self, ticker, start=None, end=None):
        try:
            url = f"{self.base_url}/history"
            params = {"ticker": ticker.upper()}
            if start:
                params["start"] = start
            if end:
                params["end"] = end

            response = self.http_client.get(url, params=params, timeout=5)

            if response.status_code == 404:
                raise TickerNotFoundError(ticker)

            response.raise_for_status()
            data = response.json()

            logger.info(f"Retrieved history for {ticker} from yahoo-finance-emulator")
            return data
        except TickerNotFoundError:
            raise
        except Exception as e:
            raise FinanceApiError(ticker, "yahoo-finance-emulator")
