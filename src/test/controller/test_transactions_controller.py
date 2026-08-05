import pytest
import json
from unittest.mock import patch
from flask import Flask
from controller.transactions_controller import transactions_bp
from dto.transactions_dto import TransactionsDTO
from exception.validation_exceptions import (
    InsufficientFundsException,
    InvalidQuantityException,
    InvalidPriceException,
    InvalidTransactionTypeException,
    PortfolioNotFoundException,
    AssetNotFoundException,
    ValidationException,
    InsufficientAssetQuantityException
)


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = Flask(__name__)
    app.register_blueprint(transactions_bp)
    return app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


@patch('controller.transactions_controller.transactions_service')
def test_get_all_transactions(mock_service, app):
    """Test GET /transactions/all endpoint."""
    transaction1 = TransactionsDTO(1, 1, "PIZZA", "BUY", 10, 150.00, "2024-01-15", 1500.00, 1500.00)
    transaction2 = TransactionsDTO(1, 1, "PIZZA", "SELL", 5, 250.00, "2024-01-20", 1250.00, 2750.00)
            
    mock_service.get_all.return_value = [transaction1, transaction2]

    with app.test_client() as client:
        response = client.get('/transactions/all')
        data = response.json

        assert response.status_code == 200
        assert len(data) == 2
        assert data[0]["transaction_type"] == "BUY"
        assert data[1]["transaction_type"] == "SELL"
        mock_service.get_all.assert_called_once()


@patch('controller.transactions_controller.transactions_service')
def test_get_all_transactions_empty(mock_service, app):
    """Test GET /transactions/all with empty list."""
    mock_service.get_all.return_value = []

    with app.test_client() as client:
        response = client.get('/transactions/all')
        data = response.json

        assert response.status_code == 200
        assert len(data) == 0
        mock_service.get_all.assert_called_once()


@patch('controller.transactions_controller.transactions_service')
def test_get_transactions_count(mock_service, app):
    """Test GET /transactions/count endpoint."""
    mock_service.count.return_value = 10

    with app.test_client() as client:
        response = client.get('/transactions/count')
        data = response.json

        assert response.status_code == 200
        assert data["count"] == 10
        mock_service.count.assert_called_once()


class TestCreateTransactionValidations:
    """Test transaction creation with validation."""

    @patch('controller.transactions_controller.transactions_service')
    def test_create_transaction_missing_required_fields(self, mock_service, client):
        """Test POST /transactions/create with missing required fields."""
        response = client.post('/transactions/create',
                              data=json.dumps({"portfolio_id": 1}),
                              content_type='application/json')

        assert response.status_code == 400
        assert "Missing required fields" in response.json["error"]
        mock_service.create_transaction.assert_not_called()

    @patch('controller.transactions_controller.transactions_service')
    def test_create_transaction_insufficient_funds(self, mock_service, client):
        """Test POST /transactions/create with insufficient funds."""
        mock_service.create_transaction.side_effect = InsufficientFundsException(100, 50)

        response = client.post('/transactions/create',
                              data=json.dumps({
                                  "portfolio_id": 1,
                                  "asset_id": "PIZZA001",
                                  "transaction_type": "BUY",
                                  "quantity": 5,
                                  "price": 10.00
                              }),
                              content_type='application/json')

        assert response.status_code == 400
        assert "Insufficient funds" in response.json["error"]
        assert "$100.00" in response.json["error"]
        assert "$50.00" in response.json["error"]

    @patch('controller.transactions_controller.transactions_service')
    def test_create_transaction_invalid_quantity(self, mock_service, client):
        """Test POST /transactions/create with invalid quantity."""
        mock_service.create_transaction.side_effect = InvalidQuantityException(-5)

        response = client.post('/transactions/create',
                              data=json.dumps({
                                  "portfolio_id": 1,
                                  "asset_id": "PIZZA001",
                                  "transaction_type": "BUY",
                                  "quantity": -5,
                                  "price": 10.00
                              }),
                              content_type='application/json')

        assert response.status_code == 400
        assert "Invalid quantity" in response.json["error"]

    @patch('controller.transactions_controller.transactions_service')
    def test_create_transaction_zero_quantity(self, mock_service, client):
        """Test POST /transactions/create with zero quantity."""
        mock_service.create_transaction.side_effect = InvalidQuantityException(0)

        response = client.post('/transactions/create',
                              data=json.dumps({
                                  "portfolio_id": 1,
                                  "asset_id": "PIZZA001",
                                  "transaction_type": "BUY",
                                  "quantity": 0,
                                  "price": 10.00
                              }),
                              content_type='application/json')

        assert response.status_code == 400
        assert "Invalid quantity: 0" in response.json["error"]

    @patch('controller.transactions_controller.transactions_service')
    def test_create_transaction_invalid_price(self, mock_service, client):
        """Test POST /transactions/create with invalid price."""
        mock_service.create_transaction.side_effect = InvalidPriceException(-10)

        response = client.post('/transactions/create',
                              data=json.dumps({
                                  "portfolio_id": 1,
                                  "asset_id": "PIZZA001",
                                  "transaction_type": "BUY",
                                  "quantity": 5,
                                  "price": -10.00
                              }),
                              content_type='application/json')

        assert response.status_code == 400
        assert "Invalid price" in response.json["error"]

    @patch('controller.transactions_controller.transactions_service')
    def test_create_transaction_zero_price(self, mock_service, client):
        """Test POST /transactions/create with zero price."""
        mock_service.create_transaction.side_effect = InvalidPriceException(0)

        response = client.post('/transactions/create',
                              data=json.dumps({
                                  "portfolio_id": 1,
                                  "asset_id": "PIZZA001",
                                  "transaction_type": "BUY",
                                  "quantity": 5,
                                  "price": 0
                              }),
                              content_type='application/json')

        assert response.status_code == 400
        assert "Invalid price: $0" in response.json["error"]

    @patch('controller.transactions_controller.transactions_service')
    def test_create_transaction_invalid_type(self, mock_service, client):
        """Test POST /transactions/create with invalid transaction type."""
        mock_service.create_transaction.side_effect = InvalidTransactionTypeException("TRADE")

        response = client.post('/transactions/create',
                              data=json.dumps({
                                  "portfolio_id": 1,
                                  "asset_id": "PIZZA001",
                                  "transaction_type": "TRADE",
                                  "quantity": 5,
                                  "price": 10.00
                              }),
                              content_type='application/json')

        assert response.status_code == 400
        assert "Invalid transaction type 'TRADE'" in response.json["error"]
        assert "BUY, SELL" in response.json["error"]

    @patch('controller.transactions_controller.transactions_service')
    def test_create_transaction_portfolio_not_found(self, mock_service, client):
        """Test POST /transactions/create with nonexistent portfolio."""
        mock_service.create_transaction.side_effect = PortfolioNotFoundException(999)

        response = client.post('/transactions/create',
                              data=json.dumps({
                                  "portfolio_id": 999,
                                  "asset_id": "PIZZA001",
                                  "transaction_type": "BUY",
                                  "quantity": 5,
                                  "price": 10.00
                              }),
                              content_type='application/json')

        assert response.status_code == 404
        assert "Portfolio with ID 999 not found" in response.json["error"]

    @patch('controller.transactions_controller.transactions_service')
    def test_create_transaction_asset_not_found(self, mock_service, client):
        """Test POST /transactions/create with nonexistent asset."""
        mock_service.create_transaction.side_effect = AssetNotFoundException("INVALID")

        response = client.post('/transactions/create',
                              data=json.dumps({
                                  "portfolio_id": 1,
                                  "asset_id": "INVALID",
                                  "transaction_type": "BUY",
                                  "quantity": 5,
                                  "price": 10.00
                              }),
                              content_type='application/json')

        assert response.status_code == 404
        assert "Asset with ID 'INVALID' not found" in response.json["error"]

    @patch('controller.transactions_controller.transactions_service')
    def test_create_transaction_validation_exception(self, mock_service, client):
        """Test POST /transactions/create with generic validation exception."""
        mock_service.create_transaction.side_effect = ValidationException("Database error")

        response = client.post('/transactions/create',
                              data=json.dumps({
                                  "portfolio_id": 1,
                                  "asset_id": "PIZZA001",
                                  "transaction_type": "BUY",
                                  "quantity": 5,
                                  "price": 10.00
                              }),
                              content_type='application/json')

        assert response.status_code == 400
        assert "Database error" in response.json["error"]

    @patch('controller.transactions_controller.transactions_service')
    def test_create_transaction_unexpected_error(self, mock_service, client):
        """Test POST /transactions/create with unexpected error."""
        mock_service.create_transaction.side_effect = RuntimeError("Unexpected error")

        response = client.post('/transactions/create',
                              data=json.dumps({
                                  "portfolio_id": 1,
                                  "asset_id": "PIZZA001",
                                  "transaction_type": "BUY",
                                  "quantity": 5,
                                  "price": 10.00
                              }),
                              content_type='application/json')

        assert response.status_code == 500
        assert "Internal server error" in response.json["error"]

    @patch('controller.transactions_controller.transactions_service')
    def test_create_transaction_success(self, mock_service, client):
        """Test successful transaction creation."""
        mock_service.create_transaction.return_value = 42

        response = client.post('/transactions/create',
                              data=json.dumps({
                                  "portfolio_id": 1,
                                  "asset_id": "PIZZA001",
                                  "transaction_type": "BUY",
                                  "quantity": 5,
                                  "price": 10.00
                              }),
                              content_type='application/json')

        assert response.status_code == 201
        assert response.json["message"] == "Transaction created successfully"
        assert response.json["transaction_id"] == 42
        mock_service.create_transaction.assert_called_once_with(1, "PIZZA001", "BUY", 5, 10.00)

    @patch('controller.transactions_controller.transactions_service')
    def test_create_buy_transaction_success(self, mock_service, client):
        """Test successful BUY transaction creation."""
        mock_service.create_transaction.return_value = 1

        response = client.post('/transactions/create',
                              data=json.dumps({
                                  "portfolio_id": 1,
                                  "asset_id": "PIZZA001",
                                  "transaction_type": "BUY",
                                  "quantity": 5,
                                  "price": 12.50
                              }),
                              content_type='application/json')

        assert response.status_code == 201
        assert response.json["transaction_id"] == 1

    @patch('controller.transactions_controller.transactions_service')
    def test_create_sell_transaction_success(self, mock_service, client):
        """Test successful SELL transaction creation."""
        mock_service.create_transaction.return_value = 2

        response = client.post('/transactions/create',
                              data=json.dumps({
                                  "portfolio_id": 1,
                                  "asset_id": "PIZZA001",
                                  "transaction_type": "SELL",
                                  "quantity": 3,
                                  "price": 8.00
                              }),
                              content_type='application/json')

        assert response.status_code == 201
        assert response.json["transaction_id"] == 2
        mock_service.create_transaction.assert_called_once_with(1, "PIZZA001", "SELL", 3, 8.00)

    @patch('controller.transactions_controller.transactions_service')
    def test_create_transaction_with_decimal_values(self, mock_service, client):
        """Test transaction creation with decimal quantity and price."""
        mock_service.create_transaction.return_value = 3

        response = client.post('/transactions/create',
                              data=json.dumps({
                                  "portfolio_id": 1,
                                  "asset_id": "PIZZA001",
                                  "transaction_type": "BUY",
                                  "quantity": 2.5,
                                  "price": 12.75
                              }),
                              content_type='application/json')

        assert response.status_code == 201
        mock_service.create_transaction.assert_called_once_with(1, "PIZZA001", "BUY", 2.5, 12.75)

    def test_create_transaction_with_empty_json(self, client):
        """Test POST /transactions/create with empty JSON object."""
        response = client.post('/transactions/create',
                              data=json.dumps({}),
                              content_type='application/json')

        assert response.status_code == 400
        assert "Missing required fields" in response.json["error"]

    @patch('controller.transactions_controller.transactions_service')
    def test_create_transaction_with_extra_fields(self, mock_service, client):
        """Test that extra fields in request are ignored."""
        mock_service.create_transaction.return_value = 4

        response = client.post('/transactions/create',
                              data=json.dumps({
                                  "portfolio_id": 1,
                                  "asset_id": "PIZZA001",
                                  "transaction_type": "BUY",
                                  "quantity": 5,
                                  "price": 10.00,
                                  "extra_field": "should be ignored",
                                  "another_field": 123
                              }),
                              content_type='application/json')

        assert response.status_code == 201
        assert response.json["transaction_id"] == 4
        mock_service.create_transaction.assert_called_once_with(1, "PIZZA001", "BUY", 5, 10.00)

    @patch('controller.transactions_controller.transactions_service')
    def test_create_sell_transaction_insufficient_inventory(self, mock_service, client):
        """Test SELL transaction fails with insufficient inventory."""
        mock_service.create_transaction.side_effect = InsufficientAssetQuantityException("PIZZA", 50, 30)

        response = client.post('/transactions/create',
                              data=json.dumps({
                                  "portfolio_id": 1,
                                  "asset_id": "PIZZA",
                                  "transaction_type": "SELL",
                                  "quantity": 50,
                                  "price": 10.00
                              }),
                              content_type='application/json')

        assert response.status_code == 400
        assert "Insufficient PIZZA" in response.json["error"]
        assert "50" in response.json["error"]
        assert "30" in response.json["error"]


# Tests for Holdings Endpoints
class TestHoldingsEndpoints:
    """Test portfolio holdings endpoints."""

    @patch('controller.transactions_controller.transactions_service')
    def test_get_portfolio_holdings_success(self, mock_service, client):
        """Test GET /transactions/portfolio/{id}/holdings with assets."""
        holdings = [
            {"asset_id": "AAPL", "quantity": 120},
            {"asset_id": "MSFT", "quantity": 70}
        ]
        mock_service.get_portfolio_holdings.return_value = holdings

        response = client.get('/transactions/portfolio/1/holdings')

        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]["asset_id"] == "AAPL"
        assert response.json[0]["quantity"] == 120
        assert response.json[1]["asset_id"] == "MSFT"
        assert response.json[1]["quantity"] == 70
        mock_service.get_portfolio_holdings.assert_called_once_with(1)

    @patch('controller.transactions_controller.transactions_service')
    def test_get_portfolio_holdings_empty(self, mock_service, client):
        """Test GET /transactions/portfolio/{id}/holdings with no assets."""
        mock_service.get_portfolio_holdings.return_value = []

        response = client.get('/transactions/portfolio/1/holdings')

        assert response.status_code == 200
        assert response.json == []
        mock_service.get_portfolio_holdings.assert_called_once_with(1)

    @patch('controller.transactions_controller.transactions_service')
    def test_get_portfolio_holdings_portfolio_not_found(self, mock_service, client):
        """Test GET /transactions/portfolio/{id}/holdings with invalid portfolio."""
        mock_service.get_portfolio_holdings.side_effect = PortfolioNotFoundException(999)

        response = client.get('/transactions/portfolio/999/holdings')

        assert response.status_code == 404
        assert "Portfolio with ID 999 not found" in response.json["error"]

    @patch('controller.transactions_controller.transactions_service')
    def test_get_portfolio_holdings_unexpected_error(self, mock_service, client):
        """Test GET /transactions/portfolio/{id}/holdings with unexpected error."""
        mock_service.get_portfolio_holdings.side_effect = RuntimeError("Database error")

        response = client.get('/transactions/portfolio/1/holdings')

        assert response.status_code == 500
        assert "Internal server error" in response.json["error"]

    @patch('controller.transactions_controller.transactions_service')
    def test_get_asset_holding_success(self, mock_service, client):
        """Test GET /transactions/portfolio/{portfolio_id}/holdings/{asset_id} success."""
        holding = {"asset_id": "AAPL", "quantity": 100}
        mock_service.get_asset_holding.return_value = holding

        response = client.get('/transactions/portfolio/1/holdings/AAPL')

        assert response.status_code == 200
        assert response.json["asset_id"] == "AAPL"
        assert response.json["quantity"] == 100
        mock_service.get_asset_holding.assert_called_once_with(1, "AAPL")

    @patch('controller.transactions_controller.transactions_service')
    def test_get_asset_holding_zero_quantity(self, mock_service, client):
        """Test GET /transactions/portfolio/{id}/holdings/{asset_id} with zero quantity."""
        holding = {"asset_id": "UNKNOWN", "quantity": 0}
        mock_service.get_asset_holding.return_value = holding

        response = client.get('/transactions/portfolio/1/holdings/UNKNOWN')

        assert response.status_code == 200
        assert response.json["quantity"] == 0

    @patch('controller.transactions_controller.transactions_service')
    def test_get_asset_holding_portfolio_not_found(self, mock_service, client):
        """Test GET /transactions/portfolio/{id}/holdings/{asset_id} with invalid portfolio."""
        mock_service.get_asset_holding.side_effect = PortfolioNotFoundException(999)

        response = client.get('/transactions/portfolio/999/holdings/AAPL')

        assert response.status_code == 404
        assert "Portfolio with ID 999 not found" in response.json["error"]

    @patch('controller.transactions_controller.transactions_service')
    def test_get_asset_holding_asset_not_found(self, mock_service, client):
        """Test GET /transactions/portfolio/{id}/holdings/{asset_id} with invalid asset."""
        mock_service.get_asset_holding.side_effect = AssetNotFoundException("INVALID")

        response = client.get('/transactions/portfolio/1/holdings/INVALID')

        assert response.status_code == 404
        assert "Asset with ID 'INVALID' not found" in response.json["error"]

    @patch('controller.transactions_controller.transactions_service')
    def test_get_asset_holding_unexpected_error(self, mock_service, client):
        """Test GET /transactions/portfolio/{id}/holdings/{asset_id} with unexpected error."""
        mock_service.get_asset_holding.side_effect = RuntimeError("Database error")

        response = client.get('/transactions/portfolio/1/holdings/AAPL')

        assert response.status_code == 500
        assert "Internal server error" in response.json["error"]
