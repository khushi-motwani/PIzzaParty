import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime
from service.transactions_service import TransactionsService
from dto.portfolios_dto import PortfoliosDTO
from dto.assets_dto import AssetsDTO
from exception.validation_exceptions import (
    InvalidQuantityException,
    InvalidPriceException,
    InvalidTransactionTypeException,
    InsufficientFundsException,
    PortfolioNotFoundException,
    AssetNotFoundException,
    ValidationException
)


class TestTransactionsService:
    """Test TransactionsService validation logic."""

    @pytest.fixture
    def service(self):
        """Create service with mocked DAOs."""
        with patch('service.transactions_service.TransactionsDao'), \
             patch('service.transactions_service.PortfoliosDao'), \
             patch('service.transactions_service.AssetsDao'):
            return TransactionsService()

    @pytest.fixture
    def mock_portfolio(self):
        """Create a mock portfolio with balance."""
        return PortfoliosDTO(
            portfolio_name="Test Portfolio",
            portfolio_balance=Decimal("1000.00"),
            portfolio_id=1
        )

    @pytest.fixture
    def mock_asset(self):
        """Create a mock asset."""
        return AssetsDTO(
            asset_name="PIZZA001",
            asset_type="FOOD",
            asset_id="PIZZA001"
        )

    # Quantity Validation Tests
    def test_create_transaction_with_negative_quantity(self, service):
        """Test that negative quantity raises InvalidQuantityException."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=PortfoliosDTO("Test", portfolio_balance=Decimal("1000")))

        with pytest.raises(InvalidQuantityException) as exc_info:
            service.create_transaction(1, "PIZZA001", "BUY", -5, 10.00)

        assert "Invalid quantity: -5" in str(exc_info.value)

    def test_create_transaction_with_zero_quantity(self, service):
        """Test that zero quantity raises InvalidQuantityException."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=PortfoliosDTO("Test", portfolio_balance=Decimal("1000")))

        with pytest.raises(InvalidQuantityException) as exc_info:
            service.create_transaction(1, "PIZZA001", "BUY", 0, 10.00)

        assert "Quantity must be a positive number" in str(exc_info.value)

    def test_create_transaction_with_non_numeric_quantity(self, service):
        """Test that non-numeric quantity raises InvalidQuantityException."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=PortfoliosDTO("Test", portfolio_balance=Decimal("1000")))

        with pytest.raises(InvalidQuantityException):
            service.create_transaction(1, "PIZZA001", "BUY", "invalid", 10.00)

    # Price Validation Tests
    def test_create_transaction_with_negative_price(self, service):
        """Test that negative price raises InvalidPriceException."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=PortfoliosDTO("Test", portfolio_balance=Decimal("1000")))

        with pytest.raises(InvalidPriceException) as exc_info:
            service.create_transaction(1, "PIZZA001", "BUY", 5, -10.00)

        assert "Invalid price: $-10.0" in str(exc_info.value)

    def test_create_transaction_with_zero_price(self, service):
        """Test that zero price raises InvalidPriceException."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=PortfoliosDTO("Test", portfolio_balance=Decimal("1000")))

        with pytest.raises(InvalidPriceException) as exc_info:
            service.create_transaction(1, "PIZZA001", "BUY", 5, 0)

        assert "Price must be a positive number" in str(exc_info.value)

    def test_create_transaction_with_non_numeric_price(self, service):
        """Test that non-numeric price raises InvalidPriceException."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=PortfoliosDTO("Test", portfolio_balance=Decimal("1000")))

        with pytest.raises(InvalidPriceException):
            service.create_transaction(1, "PIZZA001", "BUY", 5, "invalid")

    # Transaction Type Validation Tests
    def test_create_transaction_with_invalid_type(self, service):
        """Test that invalid transaction type raises InvalidTransactionTypeException."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=PortfoliosDTO("Test", portfolio_balance=Decimal("1000")))

        with pytest.raises(InvalidTransactionTypeException) as exc_info:
            service.create_transaction(1, "PIZZA001", "TRADE", 5, 10.00)

        assert "Invalid transaction type 'TRADE'" in str(exc_info.value)
        assert "BUY, SELL" in str(exc_info.value)

    def test_create_transaction_with_valid_buy_type(self, service):
        """Test that BUY is a valid transaction type."""
        mock_portfolio = PortfoliosDTO("Test", 1, portfolio_balance=Decimal("1000"))
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=AssetsDTO("PIZZA", asset_id="PIZZA001"))
        service.transactions_dao.create = MagicMock(return_value=1)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)

        transaction_id = service.create_transaction(1, "PIZZA001", "BUY", 5, 10.00)
        assert transaction_id == 1

    def test_create_transaction_with_valid_sell_type(self, service):
        """Test that SELL is a valid transaction type."""
        mock_portfolio = PortfoliosDTO("Test", 1, portfolio_balance=Decimal("1000"))
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=AssetsDTO("PIZZA", asset_id="PIZZA001"))
        service.transactions_dao.create = MagicMock(return_value=1)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)

        transaction_id = service.create_transaction(1, "PIZZA001", "SELL", 5, 10.00)
        assert transaction_id == 1

    # Portfolio Validation Tests
    def test_create_transaction_with_nonexistent_portfolio(self, service):
        """Test that nonexistent portfolio raises PortfolioNotFoundException."""
        service.portfolios_dao.get_by_id = MagicMock(
            side_effect=PortfolioNotFoundException(999)
        )

        with pytest.raises(PortfolioNotFoundException) as exc_info:
            service.create_transaction(999, "PIZZA001", "BUY", 5, 10.00)

        assert "Portfolio with ID 999 not found" in str(exc_info.value)

    # Asset Validation Tests
    def test_create_transaction_with_nonexistent_asset(self, service):
        """Test that nonexistent asset raises AssetNotFoundException."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=PortfoliosDTO("Test", portfolio_balance=Decimal("1000")))
        service.assets_dao.get_by_id = MagicMock(
            side_effect=AssetNotFoundException("INVALID")
        )

        with pytest.raises(AssetNotFoundException) as exc_info:
            service.create_transaction(1, "INVALID", "BUY", 5, 10.00)

        assert "Asset with ID 'INVALID' not found" in str(exc_info.value)

    # Insufficient Funds Tests
    def test_create_buy_transaction_with_insufficient_funds(self, service):
        """Test BUY transaction fails when balance < transaction total."""
        mock_portfolio = PortfoliosDTO("Test", 1, portfolio_balance=Decimal("50.00"))
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=AssetsDTO("PIZZA", asset_id="PIZZA001"))

        with pytest.raises(InsufficientFundsException) as exc_info:
            service.create_transaction(1, "PIZZA001", "BUY", 10, 10.00)

        assert "Insufficient funds" in str(exc_info.value)
        assert "100.00" in str(exc_info.value)  # Required
        assert "50.00" in str(exc_info.value)   # Available

    def test_create_buy_transaction_with_exact_balance(self, service):
        """Test BUY transaction succeeds when balance equals transaction total."""
        mock_portfolio = PortfoliosDTO("Test", 1, portfolio_balance=Decimal("100.00"))
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=AssetsDTO("PIZZA", asset_id="PIZZA001"))
        service.transactions_dao.create = MagicMock(return_value=1)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)

        transaction_id = service.create_transaction(1, "PIZZA001", "BUY", 10, 10.00)
        assert transaction_id == 1

    def test_create_buy_transaction_with_more_than_enough_funds(self, service):
        """Test BUY transaction succeeds when balance > transaction total."""
        mock_portfolio = PortfoliosDTO("Test", 1, portfolio_balance=Decimal("1000.00"))
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=AssetsDTO("PIZZA", asset_id="PIZZA001"))
        service.transactions_dao.create = MagicMock(return_value=1)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)

        transaction_id = service.create_transaction(1, "PIZZA001", "BUY", 5, 10.00)
        assert transaction_id == 1

    # Balance Calculation Tests
    def test_buy_transaction_calculates_new_balance_correctly(self, service):
        """Test that BUY transaction calculates balance correctly."""
        mock_portfolio = PortfoliosDTO("Test", 1, portfolio_balance=Decimal("1000.00"))
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=AssetsDTO("PIZZA", asset_id="PIZZA001"))
        service.transactions_dao.create = MagicMock(return_value=1)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)

        service.create_transaction(1, "PIZZA001", "BUY", 5, 10.00)

        # Check that update_balance was called with correct new balance
        # 1000.00 - (5 * 10.00) = 950.00
        service.portfolios_dao.update_balance.assert_called_once()
        call_args = service.portfolios_dao.update_balance.call_args
        assert call_args[0][0] == 1  # portfolio_id
        assert call_args[0][1] == Decimal("950.00")  # new_balance

    def test_sell_transaction_calculates_new_balance_correctly(self, service):
        """Test that SELL transaction calculates balance correctly."""
        mock_portfolio = PortfoliosDTO("Test", 1, portfolio_balance=Decimal("1000.00"))
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=AssetsDTO("PIZZA", asset_id="PIZZA001"))
        service.transactions_dao.create = MagicMock(return_value=1)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)

        service.create_transaction(1, "PIZZA001", "SELL", 5, 10.00)

        # Check that update_balance was called with correct new balance
        # 1000.00 + (5 * 10.00) = 1050.00
        service.portfolios_dao.update_balance.assert_called_once()
        call_args = service.portfolios_dao.update_balance.call_args
        assert call_args[0][0] == 1  # portfolio_id
        assert call_args[0][1] == Decimal("1050.00")  # new_balance

    # Successful Transaction Creation Tests
    def test_create_buy_transaction_success(self, service):
        """Test successful BUY transaction creation."""
        mock_portfolio = PortfoliosDTO("Test Portfolio", 1, portfolio_balance=Decimal("1000.00"))
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=AssetsDTO("Pizza", asset_id="PIZZA001"))
        service.transactions_dao.create = MagicMock(return_value=42)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)

        transaction_id = service.create_transaction(1, "PIZZA001", "BUY", 5, 12.50)

        assert transaction_id == 42
        service.transactions_dao.create.assert_called_once()
        service.portfolios_dao.update_balance.assert_called_once()

    def test_create_sell_transaction_success(self, service):
        """Test successful SELL transaction creation."""
        mock_portfolio = PortfoliosDTO("Test Portfolio", 1, portfolio_balance=Decimal("1000.00"))
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=AssetsDTO("Pizza", asset_id="PIZZA001"))
        service.transactions_dao.create = MagicMock(return_value=43)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)

        transaction_id = service.create_transaction(1, "PIZZA001", "SELL", 3, 8.00)

        assert transaction_id == 43
        service.transactions_dao.create.assert_called_once()
        service.portfolios_dao.update_balance.assert_called_once()

    # Database Error Tests
    def test_create_transaction_fails_when_insert_fails(self, service):
        """Test that database error during insert raises ValidationException."""
        mock_portfolio = PortfoliosDTO("Test", 1, portfolio_balance=Decimal("1000.00"))
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=AssetsDTO("PIZZA", asset_id="PIZZA001"))
        service.transactions_dao.create = MagicMock(side_effect=Exception("Database error"))

        with pytest.raises(ValidationException) as exc_info:
            service.create_transaction(1, "PIZZA001", "BUY", 5, 10.00)

        assert "Failed to create transaction" in str(exc_info.value)

    def test_create_transaction_fails_when_balance_update_fails(self, service):
        """Test that database error during balance update raises ValidationException."""
        mock_portfolio = PortfoliosDTO("Test", 1, portfolio_balance=Decimal("1000.00"))
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=AssetsDTO("PIZZA", asset_id="PIZZA001"))
        service.transactions_dao.create = MagicMock(return_value=1)
        service.portfolios_dao.update_balance = MagicMock(side_effect=Exception("Database error"))

        with pytest.raises(ValidationException) as exc_info:
            service.create_transaction(1, "PIZZA001", "BUY", 5, 10.00)

        assert "Failed to update portfolio balance" in str(exc_info.value)

    # Edge Cases
    def test_create_transaction_with_decimal_quantity(self, service):
        """Test transaction with decimal quantity."""
        mock_portfolio = PortfoliosDTO("Test", 1, portfolio_balance=Decimal("1000.00"))
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=AssetsDTO("PIZZA", asset_id="PIZZA001"))
        service.transactions_dao.create = MagicMock(return_value=1)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)

        transaction_id = service.create_transaction(1, "PIZZA001", "BUY", 2.5, 10.00)
        assert transaction_id == 1

    def test_create_transaction_with_decimal_price(self, service):
        """Test transaction with decimal price."""
        mock_portfolio = PortfoliosDTO("Test", 1, portfolio_balance=Decimal("1000.00"))
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=AssetsDTO("PIZZA", asset_id="PIZZA001"))
        service.transactions_dao.create = MagicMock(return_value=1)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)

        transaction_id = service.create_transaction(1, "PIZZA001", "BUY", 5, 12.75)
        assert transaction_id == 1

    def test_create_transaction_with_large_numbers(self, service):
        """Test transaction with large numbers."""
        mock_portfolio = PortfoliosDTO("Test", 1, portfolio_balance=Decimal("1000000.00"))
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=AssetsDTO("PIZZA", asset_id="PIZZA001"))
        service.transactions_dao.create = MagicMock(return_value=1)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)

        transaction_id = service.create_transaction(1, "PIZZA001", "BUY", 10000, 50.50)
        assert transaction_id == 1
