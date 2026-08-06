import pytest
import json
from unittest.mock import patch
from flask import Flask
from controller.portfolios_controller import portfolios_bp
from dto.portfolios_dto import PortfoliosDTO


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = Flask(__name__)
    app.register_blueprint(portfolios_bp)
    return app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


class TestGetPortfoliosEndpoints:
    """Test portfolio GET endpoints."""

    @patch('controller.portfolios_controller.portfolios_service')
    def test_get_all_portfolios(self, mock_service, client):
        """Test GET /portfolios/all."""
        portfolio1 = PortfoliosDTO("My Portfolio", 50000.00)
        portfolio2 = PortfoliosDTO("Growth Portfolio", 100000.00)

        mock_service.get_all.return_value = [portfolio1, portfolio2]

        response = client.get('/portfolios/all')

        assert response.status_code == 200
        data = response.json
        assert len(data) == 2
        assert data[0]["portfolio_name"] == "My Portfolio"
        assert data[1]["portfolio_name"] == "Growth Portfolio"
        mock_service.get_all.assert_called_once()

    @patch('controller.portfolios_controller.portfolios_service')
    def test_get_all_portfolios_empty(self, mock_service, client):
        """Test GET /portfolios/all with no portfolios."""
        mock_service.get_all.return_value = []

        response = client.get('/portfolios/all')

        assert response.status_code == 200
        data = response.json
        assert len(data) == 0
        mock_service.get_all.assert_called_once()

    @patch('controller.portfolios_controller.portfolios_service')
    def test_get_portfolios_count(self, mock_service, client):
        """Test GET /portfolios/count."""
        mock_service.count.return_value = 3

        response = client.get('/portfolios/count')

        assert response.status_code == 200
        data = response.json
        assert data["count"] == 3
        mock_service.count.assert_called_once()

    @patch('controller.portfolios_controller.portfolios_service')
    def test_get_portfolio_by_id(self, mock_service, client):
        """Test GET /portfolios/{id}."""
        portfolio = PortfoliosDTO("My Portfolio", portfolio_id=1, portfolio_balance=50000.00)
        mock_service.get_by_id.return_value = portfolio

        response = client.get('/portfolios/1')

        assert response.status_code == 200
        assert response.json["portfolio_name"] == "My Portfolio"
        assert response.json["portfolio_balance"] == 50000.00
        mock_service.get_by_id.assert_called_once_with(1)

    @patch('controller.portfolios_controller.portfolios_service')
    def test_get_portfolio_balance(self, mock_service, client):
        """Test GET /portfolios/{id}/balance."""
        portfolio = PortfoliosDTO("My Portfolio", portfolio_id=1, portfolio_balance=50000.00)
        mock_service.get_portfolio_balance.return_value = portfolio

        response = client.get('/portfolios/1/balance')

        assert response.status_code == 200
        assert response.json["portfolio_id"] == 1
        assert response.json["portfolio_balance"] == 50000.00
        mock_service.get_portfolio_balance.assert_called_once_with(1)

    @patch('controller.portfolios_controller.portfolios_service')
    def test_get_total_balance(self, mock_service, client):
        """Test GET /portfolios/total-balance."""
        mock_service.get_total_balance.return_value = 150000.00

        response = client.get('/portfolios/total-balance')

        assert response.status_code == 200
        assert response.json["total_balance"] == 150000.00
        mock_service.get_total_balance.assert_called_once()

    @patch('controller.portfolios_controller.portfolios_service')
    def test_get_sorted_by_balance_desc(self, mock_service, client):
        """Test GET /portfolios/sorted/desc."""
        portfolio1 = PortfoliosDTO("Large Portfolio", portfolio_id=1, portfolio_balance=100000.00)
        portfolio2 = PortfoliosDTO("Small Portfolio", portfolio_id=2, portfolio_balance=50000.00)

        mock_service.get_sorted_by_balance_desc.return_value = [portfolio1, portfolio2]

        response = client.get('/portfolios/sorted/desc')

        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]["portfolio_balance"] == 100000.00
        assert response.json[1]["portfolio_balance"] == 50000.00
        mock_service.get_sorted_by_balance_desc.assert_called_once()

    @patch('controller.portfolios_controller.portfolios_service')
    def test_get_sorted_by_balance_asc(self, mock_service, client):
        """Test GET /portfolios/sorted/asc."""
        portfolio1 = PortfoliosDTO("Small Portfolio", portfolio_id=1, portfolio_balance=50000.00)
        portfolio2 = PortfoliosDTO("Large Portfolio", portfolio_id=2, portfolio_balance=100000.00)

        mock_service.get_sorted_by_balance_asc.return_value = [portfolio1, portfolio2]

        response = client.get('/portfolios/sorted/asc')

        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]["portfolio_balance"] == 50000.00
        assert response.json[1]["portfolio_balance"] == 100000.00
        mock_service.get_sorted_by_balance_asc.assert_called_once()


class TestCreatePortfolioEndpoint:
    """Test portfolio creation endpoint."""

    @patch('controller.portfolios_controller.portfolios_service')
    def test_create_portfolio_success(self, mock_service, client):
        """Test POST /portfolios/create with name and balance."""
        mock_service.create.return_value = 1

        response = client.post('/portfolios/create',
                              data=json.dumps({
                                  "portfolio_name": "New Portfolio",
                                  "portfolio_balance": 50000.00
                              }),
                              content_type='application/json')

        assert response.status_code == 200
        assert response.json["message"] == "Portfolio created successfully"
        assert response.json["portfolio_id"] == 1
        mock_service.create.assert_called_once_with("New Portfolio", 50000.00)

    @patch('controller.portfolios_controller.portfolios_service')
    def test_create_portfolio_default_balance(self, mock_service, client):
        """Test POST /portfolios/create with default balance."""
        mock_service.create.return_value = 2

        response = client.post('/portfolios/create',
                              data=json.dumps({
                                  "portfolio_name": "Another Portfolio"
                              }),
                              content_type='application/json')

        assert response.status_code == 200
        assert response.json["portfolio_id"] == 2
        mock_service.create.assert_called_once_with("Another Portfolio", 0)


class TestUpdatePortfolioEndpoints:
    """Test portfolio update endpoints."""

    @patch('controller.portfolios_controller.portfolios_service')
    def test_update_portfolio_name(self, mock_service, client):
        """Test PUT /portfolios/{id}/name."""
        response = client.put('/portfolios/1/name',
                             data=json.dumps({
                                 "portfolio_name": "Updated Name"
                             }),
                             content_type='application/json')

        assert response.status_code == 200
        assert response.json["message"] == "Portfolio name updated successfully"
        assert response.json["portfolio_name"] == "Updated Name"
        assert response.json["portfolio_id"] == 1
        mock_service.update_name.assert_called_once_with(1, "Updated Name")

    @patch('controller.portfolios_controller.portfolios_service')
    def test_update_portfolio_balance(self, mock_service, client):
        """Test PUT /portfolios/{id}/balance."""
        response = client.put('/portfolios/1/balance',
                             data=json.dumps({
                                 "portfolio_balance": 75000.00
                             }),
                             content_type='application/json')

        assert response.status_code == 200
        assert response.json["message"] == "Portfolio balance updated successfully"
        assert response.json["portfolio_balance"] == 75000.00
        assert response.json["portfolio_id"] == 1
        mock_service.update_balance.assert_called_once_with(1, 75000.00)

    @patch('controller.portfolios_controller.portfolios_service')
    def test_increment_portfolio_balance(self, mock_service, client):
        """Test PUT /portfolios/{id}/increment."""
        response = client.put('/portfolios/1/increment',
                             data=json.dumps({
                                 "amount": 5000.00
                             }),
                             content_type='application/json')

        assert response.status_code == 200
        assert response.json["message"] == "Portfolio balance incremented successfully"
        assert response.json["amount"] == 5000.00
        assert response.json["portfolio_id"] == 1
        mock_service.increment_balance.assert_called_once_with(1, 5000.00)

    @patch('controller.portfolios_controller.portfolios_service')
    def test_decrement_portfolio_balance(self, mock_service, client):
        """Test PUT /portfolios/{id}/decrement."""
        response = client.put('/portfolios/1/decrement',
                             data=json.dumps({
                                 "amount": 2500.00
                             }),
                             content_type='application/json')

        assert response.status_code == 200
        assert response.json["message"] == "Portfolio balance decremented successfully"
        assert response.json["amount"] == 2500.00
        assert response.json["portfolio_id"] == 1
        mock_service.decrement_balance.assert_called_once_with(1, 2500.00)


class TestDeletePortfolioEndpoint:
    """Test portfolio deletion endpoint."""

    @patch('controller.portfolios_controller.portfolios_service')
    def test_delete_portfolio_success(self, mock_service, client):
        """Test DELETE /portfolios/{id}."""
        response = client.delete('/portfolios/1')

        assert response.status_code == 200
        assert response.json["message"] == "Portfolio deleted successfully"
        assert response.json["portfolio_id"] == 1
        mock_service.delete.assert_called_once_with(1)

    @patch('controller.portfolios_controller.portfolios_service')
    def test_delete_portfolio_not_found(self, mock_service, client):
        """Test DELETE /portfolios/{id} with invalid portfolio."""
        mock_service.delete.side_effect = ValueError("Portfolio not found")

        response = client.delete('/portfolios/999')

        assert response.status_code == 404
        assert "Portfolio not found" in response.json["error"]

    @patch('controller.portfolios_controller.portfolios_service')
    def test_delete_portfolio_error(self, mock_service, client):
        """Test DELETE /portfolios/{id} with error."""
        mock_service.delete.side_effect = RuntimeError("Database error")

        response = client.delete('/portfolios/1')

        assert response.status_code == 500
        assert "Internal server error" in response.json["error"]
