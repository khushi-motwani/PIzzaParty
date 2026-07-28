import unittest
from unittest.mock import Mock, patch
from service.finance_service import FinanceService
from dto.quote_dto import QuoteDTO
from exception.finance_exceptions import TickerNotFoundError, FinanceApiError


class TestFinanceService(unittest.TestCase):
    def test_get_quote_success(self):
        mock_client = Mock()
        expected_quote = QuoteDTO(
            ticker="AAPL",
            price=150.5,
            currency="USD",
            previous_close=149.75,
            market_cap=2400000000000,
            day_high=151.2,
            day_low=148.9
        )
        mock_client.get_quote.return_value = expected_quote

        service = FinanceService(client=mock_client)
        quote = service.get_quote("AAPL")

        self.assertEqual(quote.ticker, "AAPL")
        self.assertEqual(quote.price, 150.5)
        mock_client.get_quote.assert_called_once_with("AAPL")

    def test_get_quote_ticker_not_found(self):
        mock_client = Mock()
        mock_client.get_quote.side_effect = TickerNotFoundError("Ticker 'NOTREAL' not found")

        service = FinanceService(client=mock_client)

        with self.assertRaises(TickerNotFoundError):
            service.get_quote("NOTREAL")

    def test_get_quote_api_error(self):
        mock_client = Mock()
        mock_client.get_quote.side_effect = FinanceApiError("Network error")

        service = FinanceService(client=mock_client)

        with self.assertRaises(FinanceApiError):
            service.get_quote("AAPL")


if __name__ == '__main__':
    unittest.main()
