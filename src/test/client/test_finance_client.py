import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import requests
from client.finance_client import FinanceClient
from exception.finance_exceptions import TickerNotFoundError, FinanceApiError


class TestFinanceClientYFinance(unittest.TestCase):
    """Test yfinance as the primary data source"""

    def setUp(self):
        self.mock_ticker_factory = Mock()
        self.mock_http_client = Mock()

    def test_get_quote_yfinance_success(self):
        """yfinance returns valid data"""
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

        client = FinanceClient(ticker_factory=self.mock_ticker_factory, http_client=self.mock_http_client)
        quote = client.get_quote("AAPL")

        self.assertEqual(quote.ticker, "AAPL")
        self.assertEqual(quote.price, 150.5)
        self.assertEqual(quote.currency, "USD")
        self.assertEqual(quote.day_high, 151.2)
        self.assertEqual(quote.day_low, 148.9)
        self.mock_ticker_factory.assert_called_once_with("AAPL")
        # HTTP client should not be called when yfinance succeeds
        self.mock_http_client.get.assert_not_called()

    def test_get_quote_yfinance_empty_history(self):
        """yfinance returns empty DataFrame, falls back to cached API"""
        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame()
        self.mock_ticker_factory.return_value = mock_ticker

        mock_response = Mock()
        mock_response.json.return_value = {
            "ticker": "AAPL",
            "price_data": {
                "close": [194.5, 195.2, 195.5]
            }
        }
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(ticker_factory=self.mock_ticker_factory, http_client=self.mock_http_client)
        quote = client.get_quote("AAPL")

        self.assertEqual(quote.ticker, "AAPL")
        self.assertEqual(quote.price, 195.5)
        self.assertEqual(quote.previous_close, 195.2)
        # HTTP client should be called when yfinance fails
        self.mock_http_client.get.assert_called_once()

    def test_get_quote_yfinance_failure_cached_api_success(self):
        """yfinance fails, falls back to cached API"""
        self.mock_ticker_factory.side_effect = Exception("Network error")

        mock_response = Mock()
        mock_response.json.return_value = {
            "ticker": "AAPL",
            "price_data": {
                "close": [194.5, 195.5]
            }
        }
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(ticker_factory=self.mock_ticker_factory, http_client=self.mock_http_client)
        quote = client.get_quote("AAPL")

        self.assertEqual(quote.price, 195.5)
        self.mock_http_client.get.assert_called_once()


class TestFinanceClientFallback(unittest.TestCase):
    """Test fallback mechanisms (cached API and mock data)"""

    def setUp(self):
        self.mock_ticker_factory = Mock()
        self.mock_http_client = Mock()

    def test_fallback_to_cached_api_success(self):
        """Cached API returns valid data after yfinance fails"""
        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame()
        self.mock_ticker_factory.return_value = mock_ticker

        mock_response = Mock()
        mock_response.json.return_value = {
            "ticker": "AMZN",
            "price_data": {
                "close": [174.5, 174.8, 175.0, 175.2, 175.3]
            }
        }
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(ticker_factory=self.mock_ticker_factory, http_client=self.mock_http_client)
        quote = client.get_quote("AMZN")

        self.assertEqual(quote.ticker, "AMZN")
        self.assertEqual(quote.price, 175.3)
        self.assertEqual(quote.previous_close, 175.2)
        self.assertEqual(quote.day_high, 175.3)
        self.assertEqual(quote.day_low, 174.5)

    def test_fallback_to_mock_data_known_ticker(self):
        """Falls back to mock data when both APIs fail"""
        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame()
        self.mock_ticker_factory.return_value = mock_ticker

        # Cached API raises exception
        self.mock_http_client.get.side_effect = requests.RequestException("API unavailable")

        client = FinanceClient(ticker_factory=self.mock_ticker_factory, http_client=self.mock_http_client)
        quote = client.get_quote("AAPL")

        self.assertEqual(quote.ticker, "AAPL")
        # Should use mock data
        self.assertEqual(quote.price, 195.5)
        self.assertEqual(quote.day_high, 198.2)

    def test_fallback_to_mock_data_unknown_ticker(self):
        """Unknown ticker raises TickerNotFoundError even with fallback"""
        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame()
        self.mock_ticker_factory.return_value = mock_ticker

        self.mock_http_client.get.side_effect = requests.RequestException("API unavailable")

        client = FinanceClient(ticker_factory=self.mock_ticker_factory, http_client=self.mock_http_client)

        with self.assertRaises(TickerNotFoundError) as context:
            client.get_quote("UNKNOWNTICKER")

        self.assertIn("not found in mock data", str(context.exception))

    def test_cached_api_invalid_response(self):
        """Cached API returns invalid response, falls back to mock data"""
        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame()
        self.mock_ticker_factory.return_value = mock_ticker

        # API returns response without proper price_data structure
        mock_response = Mock()
        mock_response.json.return_value = {"ticker": "TSLA", "invalid": "data"}
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(ticker_factory=self.mock_ticker_factory, http_client=self.mock_http_client)
        quote = client.get_quote("TSLA")

        # Should fall back to mock data
        self.assertEqual(quote.price, 197.5)
        self.assertEqual(quote.day_high, 200.1)
        self.assertEqual(quote.day_low, 195.3)


class TestFinanceClientLogging(unittest.TestCase):
    """Test logging behavior"""

    def setUp(self):
        self.mock_ticker_factory = Mock()
        self.mock_http_client = Mock()

    @patch('client.finance_client.logger')
    def test_logs_yfinance_success(self, mock_logger):
        """Logs when yfinance succeeds"""
        mock_ticker = Mock()
        mock_data = pd.DataFrame({
            "Open": [150], "High": [151], "Low": [149], "Close": [150.5], "Volume": [1000000]
        })
        mock_ticker.history.return_value = mock_data
        self.mock_ticker_factory.return_value = mock_ticker

        client = FinanceClient(ticker_factory=self.mock_ticker_factory, http_client=self.mock_http_client)
        client.get_quote("AAPL")

        mock_logger.info.assert_called_with("Retrieved data for AAPL from yfinance")

    @patch('client.finance_client.logger')
    def test_logs_cached_api_fallback(self, mock_logger):
        """Logs when falling back to cached API"""
        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame()
        self.mock_ticker_factory.return_value = mock_ticker

        mock_response = Mock()
        mock_response.json.return_value = {"price": 195.5, "day_high": 198.2, "day_low": 194.9}
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(ticker_factory=self.mock_ticker_factory, http_client=self.mock_http_client)
        client.get_quote("AAPL")

        # Should log both failure and fallback
        calls = [str(call) for call in mock_logger.method_calls]
        self.assertTrue(any("yfinance failed" in str(call) for call in calls))
        self.assertTrue(any("cached API" in str(call) for call in calls))

    @patch('client.finance_client.logger')
    def test_logs_mock_data_warning(self, mock_logger):
        """Logs warning when using mock data"""
        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame()
        self.mock_ticker_factory.return_value = mock_ticker
        self.mock_http_client.get.side_effect = requests.RequestException("API down")

        client = FinanceClient(ticker_factory=self.mock_ticker_factory, http_client=self.mock_http_client)
        client.get_quote("AAPL")

        mock_logger.warning.assert_called()
        self.assertIn("mock data", str(mock_logger.warning.call_args))


if __name__ == '__main__':
    unittest.main()
