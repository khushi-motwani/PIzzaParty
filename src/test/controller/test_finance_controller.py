import pytest
from unittest.mock import patch
from flask import Flask
from controller.finance_controller import finance_bp
from dto.quote_dto import QuoteDTO
from exception.finance_exceptions import TickerNotFoundError, FinanceApiError


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = Flask(__name__)
    app.register_blueprint(finance_bp)
    return app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


class TestGetQuoteEndpoint:
    """Test GET /finance/quote endpoint."""

    @patch('controller.finance_controller.finance_service')
    def test_get_quote_success(self, mock_service, client):
        """Test successful quote retrieval."""
        quote = QuoteDTO(
            ticker="AAPL",
            price=150.5,
            currency="USD",
            previous_close=149.75,
            market_cap=2400000000000,
            day_high=151.2,
            day_low=148.9
        )
        mock_service.get_quote.return_value = quote

        response = client.get('/finance/quote/AAPL')

        assert response.status_code == 200
        data = response.json
        assert data["ticker"] == "AAPL"
        assert data["price"] == 150.5
        assert data["currency"] == "USD"
        assert data["day_high"] == 151.2
        assert data["day_low"] == 148.9
        mock_service.get_quote.assert_called_once_with("AAPL")

    @patch('controller.finance_controller.finance_service')
    def test_get_quote_ticker_not_found(self, mock_service, client):
        """Test quote retrieval with invalid ticker."""
        mock_service.get_quote.side_effect = TickerNotFoundError("Ticker 'NOTREAL' not found or has no price data")

        response = client.get('/finance/quote/NOTREAL')

        assert response.status_code == 404
        assert "error" in response.json
        assert "not found" in response.json["error"]
        mock_service.get_quote.assert_called_once_with("NOTREAL")

    @patch('controller.finance_controller.finance_service')
    def test_get_quote_api_error(self, mock_service, client):
        """Test quote retrieval with API error."""
        mock_service.get_quote.side_effect = FinanceApiError("Failed to fetch quote for ticker 'AAPL': Network error")

        response = client.get('/finance/quote/AAPL')

        assert response.status_code == 502
        assert "error" in response.json
        assert "Network error" in response.json["error"]
        mock_service.get_quote.assert_called_once_with("AAPL")


class TestGetHistoryEndpoint:
    """Test GET /finance/history endpoint."""

    @patch('controller.finance_controller.finance_service')
    def test_get_history_success(self, mock_service, client):
        """Test successful history retrieval."""
        history = [
            {"date": "2024-01-01", "price": 150.0},
            {"date": "2024-01-02", "price": 151.5},
            {"date": "2024-01-03", "price": 149.8}
        ]
        mock_service.get_history.return_value = history

        response = client.get('/finance/history/AAPL?start=2024-01-01&end=2024-01-03')

        assert response.status_code == 200
        data = response.json
        assert len(data) == 3
        assert data[0]["date"] == "2024-01-01"
        assert data[0]["price"] == 150.0
        mock_service.get_history.assert_called_once_with("AAPL", "2024-01-01", "2024-01-03")

    @patch('controller.finance_controller.finance_service')
    def test_get_history_without_dates(self, mock_service, client):
        """Test history retrieval without start/end dates."""
        history = [{"date": "2024-01-01", "price": 150.0}]
        mock_service.get_history.return_value = history

        response = client.get('/finance/history/AAPL')

        assert response.status_code == 200
        mock_service.get_history.assert_called_once_with("AAPL", None, None)

    @patch('controller.finance_controller.finance_service')
    def test_get_history_ticker_not_found(self, mock_service, client):
        """Test history retrieval with invalid ticker."""
        mock_service.get_history.side_effect = TickerNotFoundError("Ticker 'INVALID' not found")

        response = client.get('/finance/history/INVALID?start=2024-01-01&end=2024-01-03')

        assert response.status_code == 404
        assert "error" in response.json
        mock_service.get_history.assert_called_once_with("INVALID", "2024-01-01", "2024-01-03")

    @patch('controller.finance_controller.finance_service')
    def test_get_history_api_error(self, mock_service, client):
        """Test history retrieval with API error."""
        mock_service.get_history.side_effect = FinanceApiError("Service unavailable")

        response = client.get('/finance/history/AAPL?start=2024-01-01&end=2024-01-03')

        assert response.status_code == 502
        assert "error" in response.json
        assert "Service unavailable" in response.json["error"]

    @patch('controller.finance_controller.finance_service')
    def test_get_history_empty_result(self, mock_service, client):
        """Test history retrieval with no results."""
        mock_service.get_history.return_value = []

        response = client.get('/finance/history/AAPL?start=2024-01-01&end=2024-01-03')

        assert response.status_code == 200
        assert response.json == []
