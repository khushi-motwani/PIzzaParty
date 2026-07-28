import unittest
from unittest.mock import Mock, patch
import pandas as pd
from client.finance_client import FinanceClient
from exception.finance_exceptions import TickerNotFoundError, FinanceApiError


class TestFinanceClient(unittest.TestCase):
    def setUp(self):
        self.mock_ticker_factory = Mock()

    def test_get_quote_success(self):
        mock_ticker = Mock()
        mock_data = pd.DataFrame({
            "Open": [149.5],
            "High": [151.2],
            "Low": [148.9],
            "Close": [150.5],
            "Volume": [1000000]
        })
        mock_ticker.history.return_value = mock_data
        self.mock_ticker_factory.return_value = mock_ticker

        client = FinanceClient(ticker_factory=self.mock_ticker_factory)
        quote = client.get_quote("AAPL")

        self.assertEqual(quote.ticker, "AAPL")
        self.assertEqual(quote.price, 150.5)
        self.assertEqual(quote.currency, "USD")
        self.assertEqual(quote.day_high, 151.2)
        self.assertEqual(quote.day_low, 148.9)
        self.mock_ticker_factory.assert_called_once_with("AAPL")

    def test_get_quote_empty_history(self):
        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame()
        self.mock_ticker_factory.return_value = mock_ticker

        client = FinanceClient(ticker_factory=self.mock_ticker_factory)

        with self.assertRaises(TickerNotFoundError):
            client.get_quote("NOTAREALTICKER")

    def test_get_quote_none_history(self):
        mock_ticker = Mock()
        mock_ticker.history.return_value = None
        self.mock_ticker_factory.return_value = mock_ticker

        client = FinanceClient(ticker_factory=self.mock_ticker_factory)

        with self.assertRaises(TickerNotFoundError):
            client.get_quote("INVALIDTICKER")

    def test_get_quote_api_error(self):
        self.mock_ticker_factory.side_effect = Exception("Network error")

        client = FinanceClient(ticker_factory=self.mock_ticker_factory)

        with self.assertRaises(FinanceApiError):
            client.get_quote("AAPL")

    def test_get_quote_history_error(self):
        mock_ticker = Mock()
        mock_ticker.history.side_effect = Exception("API timeout")
        self.mock_ticker_factory.return_value = mock_ticker

        client = FinanceClient(ticker_factory=self.mock_ticker_factory)

        with self.assertRaises(FinanceApiError):
            client.get_quote("AAPL")


if __name__ == '__main__':
    unittest.main()
