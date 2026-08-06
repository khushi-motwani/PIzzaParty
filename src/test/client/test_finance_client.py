import unittest
from unittest.mock import Mock, patch
import requests
from client.finance_client import FinanceClient
from exception.finance_exceptions import TickerNotFoundError, FinanceApiError


class TestFinanceClientSuccess(unittest.TestCase):
    """Test successful quote retrieval from the emulator API"""

    def setUp(self):
        self.mock_http_client = Mock()

    def test_get_quote_success(self):
        """Successfully fetch quote from the finance emulator"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
            "currency": "USD",
            "price": 150.5,
            "previousClose": 149.75,
            "change": 0.75,
            "changePercent": 0.50,
            "dayHigh": 151.2,
            "dayLow": 148.9,
            "fiftyTwoWeekHigh": 199.0,
            "fiftyTwoWeekLow": 120.0,
            "volume": 1000000,
            "asOf": "2024-01-15"
        }
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")
        quote = client.get_quote("AAPL")

        self.assertEqual(quote.ticker, "AAPL")
        self.assertEqual(quote.price, 150.5)
        self.assertEqual(quote.currency, "USD")
        self.assertEqual(quote.previous_close, 149.75)
        self.assertEqual(quote.day_high, 151.2)
        self.assertEqual(quote.day_low, 148.9)
        self.assertIsNone(quote.market_cap)

        # Verify the correct API call was made
        self.mock_http_client.get.assert_called_once_with(
            "http://test:4000/quote",
            params={"ticker": "AAPL"},
            timeout=5
        )

    def test_get_quote_lowercase_ticker(self):
        """Uppercase ticker before sending to API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ticker": "TSLA",
            "price": 197.5,
            "currency": "USD",
            "previousClose": 196.2,
            "dayHigh": 200.1,
            "dayLow": 195.3
        }
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")
        quote = client.get_quote("tsla")

        self.assertEqual(quote.ticker, "tsla")
        self.assertEqual(quote.price, 197.5)

        # Verify ticker was uppercased in the API call
        self.mock_http_client.get.assert_called_once_with(
            "http://test:4000/quote",
            params={"ticker": "TSLA"},
            timeout=5
        )

    def test_get_quote_uses_default_base_url(self):
        """Use localhost:4000 as default base URL"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ticker": "MSFT",
            "price": 445.2,
            "currency": "USD",
            "previousClose": 443.1,
            "dayHigh": 450.0,
            "dayLow": 442.1
        }
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(http_client=self.mock_http_client)
        quote = client.get_quote("MSFT")

        self.assertEqual(quote.price, 445.2)

        # Verify default URL was used
        call_args = self.mock_http_client.get.call_args
        self.assertIn("http://localhost:4000", call_args[0][0])


class TestFinanceClientErrors(unittest.TestCase):
    """Test error handling"""

    def setUp(self):
        self.mock_http_client = Mock()

    def test_get_quote_ticker_not_found(self):
        """404 response raises TickerNotFoundError"""
        mock_response = Mock()
        mock_response.status_code = 404
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")

        with self.assertRaises(TickerNotFoundError) as context:
            client.get_quote("UNKNOWNTICKER")

        self.assertIn("UNKNOWNTICKER", str(context.exception))

    def test_get_quote_network_error(self):
        """Network error raises FinanceApiError"""
        self.mock_http_client.get.side_effect = requests.ConnectionError("Connection failed")

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")

        with self.assertRaises(FinanceApiError) as context:
            client.get_quote("AAPL")

        self.assertIn("yahoo-finance-emulator", str(context.exception))

    def test_get_quote_timeout(self):
        """Request timeout raises FinanceApiError"""
        self.mock_http_client.get.side_effect = requests.Timeout("Request timed out")

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")

        with self.assertRaises(FinanceApiError):
            client.get_quote("AAPL")

    def test_get_quote_invalid_json(self):
        """Invalid JSON response raises FinanceApiError"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")

        with self.assertRaises(FinanceApiError):
            client.get_quote("AAPL")

    def test_get_quote_http_error(self):
        """HTTP error (500, etc.) raises FinanceApiError"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("Internal Server Error")
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")

        with self.assertRaises(FinanceApiError):
            client.get_quote("AAPL")


class TestFinanceClientHistory(unittest.TestCase):
    """Test history retrieval"""

    def setUp(self):
        self.mock_http_client = Mock()

    def test_get_history_success(self):
        """Successfully fetch history from the finance API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"date": "2024-01-01", "price": 150.0, "volume": 1000000},
            {"date": "2024-01-02", "price": 151.5, "volume": 950000},
            {"date": "2024-01-03", "price": 149.8, "volume": 1100000}
        ]
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")
        history = client.get_history("AAPL", start="2024-01-01", end="2024-01-03")

        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["date"], "2024-01-01")
        self.assertEqual(history[0]["price"], 150.0)

        # Verify the correct API call was made with start and end parameters
        self.mock_http_client.get.assert_called_once()
        call_args = self.mock_http_client.get.call_args
        self.assertIn("/history", call_args[0][0])
        self.assertEqual(call_args[1]["params"]["ticker"], "AAPL")
        self.assertEqual(call_args[1]["params"]["start"], "2024-01-01")
        self.assertEqual(call_args[1]["params"]["end"], "2024-01-03")

    def test_get_history_without_dates(self):
        """Fetch history without start/end dates"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"date": "2024-01-01", "price": 150.0}]
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")
        history = client.get_history("AAPL")

        self.assertEqual(len(history), 1)
        # Verify start and end were not included in params
        call_args = self.mock_http_client.get.call_args
        params = call_args[1]["params"]
        self.assertNotIn("start", params)
        self.assertNotIn("end", params)

    def test_get_history_with_only_start_date(self):
        """Fetch history with only start date"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"date": "2024-01-01", "price": 150.0}]
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")
        history = client.get_history("AAPL", start="2024-01-01")

        call_args = self.mock_http_client.get.call_args
        params = call_args[1]["params"]
        self.assertEqual(params["start"], "2024-01-01")
        self.assertNotIn("end", params)

    def test_get_history_lowercase_ticker(self):
        """Uppercase ticker before sending to API for history"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")
        client.get_history("tsla", start="2024-01-01", end="2024-01-03")

        call_args = self.mock_http_client.get.call_args
        self.assertEqual(call_args[1]["params"]["ticker"], "TSLA")

    def test_get_history_ticker_not_found(self):
        """404 response raises TickerNotFoundError for history"""
        mock_response = Mock()
        mock_response.status_code = 404
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")

        with self.assertRaises(TickerNotFoundError) as context:
            client.get_history("UNKNOWNTICKER")

        self.assertIn("UNKNOWNTICKER", str(context.exception))

    def test_get_history_network_error(self):
        """Network error raises FinanceApiError for history"""
        self.mock_http_client.get.side_effect = requests.ConnectionError("Connection failed")

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")

        with self.assertRaises(FinanceApiError) as context:
            client.get_history("AAPL")

        self.assertIn("yahoo-finance-emulator", str(context.exception))

    def test_get_history_timeout(self):
        """Request timeout raises FinanceApiError for history"""
        self.mock_http_client.get.side_effect = requests.Timeout("Request timed out")

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")

        with self.assertRaises(FinanceApiError):
            client.get_history("AAPL")

    def test_get_history_invalid_json(self):
        """Invalid JSON response raises FinanceApiError for history"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")

        with self.assertRaises(FinanceApiError):
            client.get_history("AAPL")

    def test_get_history_http_error(self):
        """HTTP error raises FinanceApiError for history"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("Internal Server Error")
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")

        with self.assertRaises(FinanceApiError):
            client.get_history("AAPL")

    @patch('client.finance_client.logger')
    def test_logs_history_success(self, mock_logger):
        """Logs when history is successfully retrieved"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"date": "2024-01-01", "price": 150.0}]
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")
        client.get_history("AAPL")

        mock_logger.info.assert_called_with("Retrieved history for AAPL from yahoo-finance-emulator")


class TestFinanceClientLogging(unittest.TestCase):
    """Test logging behavior"""

    def setUp(self):
        self.mock_http_client = Mock()

    @patch('client.finance_client.logger')
    def test_logs_success(self, mock_logger):
        """Logs when quote is successfully retrieved"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ticker": "AAPL",
            "price": 150.5,
            "currency": "USD",
            "previousClose": 149.75,
            "dayHigh": 151.2,
            "dayLow": 148.9
        }
        self.mock_http_client.get.return_value = mock_response

        client = FinanceClient(http_client=self.mock_http_client, base_url="http://test:4000")
        client.get_quote("AAPL")

        mock_logger.info.assert_called_with("Retrieved data for AAPL from yahoo-finance-emulator")


if __name__ == '__main__':
    unittest.main()
