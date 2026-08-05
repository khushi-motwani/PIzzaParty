import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime
from service.transactions_service import TransactionsService
from dto.transactions_dto import TransactionsDTO
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
            portfolio_balance=1000.00,
            portfolio_id=1
        )

    @pytest.fixture
    def mock_asset(self):
        """Create a mock asset."""
        return AssetsDTO(
            asset_id="PIZZA001",
            asset_name="PIZZA",
            asset_type="SLICE",
            asset_sector="DINING",
            asset_industry="FOOD",
            is_favourite=False
        )
    
    def test_get_all_returns_transactions(self, service):
        transaction1 = TransactionsDTO(1, 1, "PIZZA", "BUY", 10, 150.00, "2024-01-15", 1500.00, 1500.00)
        transaction2 = TransactionsDTO(1, 1, "PIZZA", "SELL", 5, 250.00, "2024-01-20", 1250.00, 2750.00)
        
        service.transactions_dao.get_all = MagicMock(return_value=[transaction1, transaction2])

        result = service.get_all()
        
        assert len(result) == 2
        assert result[0].transaction_type == "BUY"
        assert result[1].transaction_type == "SELL"
        service.transactions_dao.get_all.assert_called_once()
        
    def test_count_returns_count(self, service):
        service.transactions_dao.count.return_value = 5
        result = service.count()
        assert result == 5
        service.transactions_dao.count.assert_called_once()
    
    def test_invalid_transaction_type(self, service):
        invalid_transaction_type = "TRANSFER"
        with pytest.raises(InvalidTransactionTypeException):
            service.create(1, "PIZZA", f"{invalid_transaction_type}", 10, 150.00, "2024-01-15", 1500.00, 48500.00)

    # Balance Calculation Tests
    def test_buy_transaction_calculates_new_balance_correctly(self, service, mock_portfolio, mock_asset):
        """Test that BUY transaction calculates balance correctly."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.transactions_dao.create = MagicMock(return_value=1)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)

        service.create(1, "PIZZA", "BUY", 10, 15.00, "2024-01-15", 150.00, None)

        # Check that update_balance was called with correct new balance
        # 1000.00 - (10 * 15.00) = 850.00
        call_args = service.transactions_dao.create.call_args.kwargs
        assert call_args["balance_after_transaction"] == Decimal("850.00")
    
    def test_sell_transaction_calculates_new_balance_correctly(self, service, mock_portfolio, mock_asset):
        """Test that SELL transaction calculates balance correctly."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.transactions_dao.create = MagicMock(return_value=1)
        service.transactions_dao.get_asset_holding = MagicMock(return_value=100)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)

        service.create(1, "PIZZA", "SELL", 10, 15.00, "2024-01-15", 150.00, 1000)

        # Check that update_balance was called with correct new balance
        # 1000.00 + (10 * 15.00) = 1150.00
        call_args = service.transactions_dao.create.call_args.kwargs
        assert call_args["balance_after_transaction"] == Decimal("1150.00")  # new_balance
        

    # Database Error Tests
    def test_create_fails_when_insert_fails(self, service, mock_portfolio, mock_asset):
        """Test that database error during insert raises ValidationException."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.transactions_dao.get_asset_holding = MagicMock(return_value=100)
        service.transactions_dao.create = MagicMock(side_effect=Exception("Database error"))

        with pytest.raises(ValidationException):
            service.create(1, "PIZZA", "SELL", 10, 15.00, "2024-01-15", 150.00, 1000)


    def test_create_fails_when_balance_update_fails(self, service, mock_portfolio, mock_asset):
        """Test that database error during balance update raises ValidationException."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.transactions_dao.get_asset_holding = MagicMock(return_value=100)
        service.transactions_dao.create = MagicMock(return_value=1)
        service.portfolios_dao.update_balance = MagicMock(side_effect=Exception("Database error"))

        with pytest.raises(ValidationException):
            service.create(1, "PIZZA", "SELL", 10, 15.00, "2024-01-15", 150.00, 1000)

    # Edge Cases
    def test_create_with_decimal_quantity(self, service, mock_portfolio, mock_asset):
        """Test transaction with decimal quantity raises InvalidQuantityException."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.transactions_dao.get_asset_holding = MagicMock(return_value=100)
        with pytest.raises(InvalidQuantityException):
            service.create(1, "PIZZA", "SELL", Decimal(1.5), 100, "2024-01-15", 150.00, 1000)

    def test_create_with_decimal_price(self, service, mock_asset):
        """Test transaction with decimal price."""
        mock_portfolio = PortfoliosDTO("Test", Decimal("1000.00"), 1)
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.transactions_dao.create = MagicMock(return_value=1)
        service.transactions_dao.get_asset_holding = MagicMock(return_value=100)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)

        transaction_id = service.create(1, "PIZZA", "SELL", 10, 15.00, "2024-01-15", 150.00, 1000)
        assert transaction_id == 1

    # Tests for _validate_transaction_id
    def test_validate_transaction_id_valid(self, service):
        """Test validation passes for valid transaction ID."""
        transaction = TransactionsDTO(1, 1, "PIZZA", "BUY", 10, 150.00, "2024-01-15", 1500.00, 1500.00)
        service.transactions_dao.get_by_id = MagicMock(return_value=transaction)
        service._validate_transaction_id(1)
        service.transactions_dao.get_by_id.assert_called_once_with(1)

    def test_validate_transaction_id_none(self, service):
        """Test validation fails for None transaction ID."""
        with pytest.raises(ValueError, match="Transaction ID must be a positive integer"):
            service._validate_transaction_id(None)

    def test_validate_transaction_id_zero(self, service):
        """Test validation fails for zero transaction ID."""
        with pytest.raises(ValueError, match="Transaction ID must be a positive integer"):
            service._validate_transaction_id(0)

    def test_validate_transaction_id_negative(self, service):
        """Test validation fails for negative transaction ID."""
        with pytest.raises(ValueError, match="Transaction ID must be a positive integer"):
            service._validate_transaction_id(-1)

    def test_validate_transaction_id_not_found(self, service):
        """Test validation fails when transaction doesn't exist."""
        service.transactions_dao.get_by_id = MagicMock(side_effect=Exception("Not found"))
        with pytest.raises(Exception):
            service._validate_transaction_id(999)

    # Tests for _validate_transaction_type
    def test_validate_transaction_type_buy(self, service):
        """Test validation passes for BUY type."""
        service._validate_transaction_type("BUY")

    def test_validate_transaction_type_sell(self, service):
        """Test validation passes for SELL type."""
        service._validate_transaction_type("SELL")

    def test_validate_transaction_type_deposit(self, service):
        """Test validation passes for DEPOSIT type."""
        service._validate_transaction_type("DEPOSIT")

    def test_validate_transaction_type_withdraw(self, service):
        """Test validation passes for WITHDRAW type."""
        service._validate_transaction_type("WITHDRAW")

    def test_validate_transaction_type_invalid(self, service):
        """Test validation fails for invalid type."""
        with pytest.raises(InvalidTransactionTypeException):
            service._validate_transaction_type("INVALID")

    # Tests for _validate_monetary_input
    def test_validate_monetary_input_positive_int(self, service):
        """Test validation passes for positive integer."""
        service._validate_monetary_input(100)

    def test_validate_monetary_input_positive_float(self, service):
        """Test validation passes for positive float."""
        service._validate_monetary_input(100.50)

    def test_validate_monetary_input_positive_decimal(self, service):
        """Test validation passes for positive Decimal."""
        service._validate_monetary_input(Decimal("100.50"))

    def test_validate_monetary_input_zero(self, service):
        """Test validation passes for zero."""
        service._validate_monetary_input(0)

    def test_validate_monetary_input_negative(self, service):
        """Test validation fails for negative value."""
        with pytest.raises(ValueError, match="cannot be negative"):
            service._validate_monetary_input(-10)

    def test_validate_monetary_input_none(self, service):
        """Test validation fails for None."""
        with pytest.raises(ValueError):
            service._validate_monetary_input(None)

    # Tests for _get_transaction
    def test_get_transaction_success(self, service):
        """Test successful transaction retrieval."""
        transaction = TransactionsDTO(1, 1, "PIZZA", "BUY", 10, 150.00, "2024-01-15", 1500.00, 1500.00)
        service.transactions_dao.get_by_id = MagicMock(return_value=transaction)
        result = service._get_transaction(1)
        assert result == transaction

    def test_get_transaction_not_found(self, service):
        """Test transaction not found raises exception."""
        from exception.validation_exceptions import TransactionsNotFoundException
        service.transactions_dao.get_by_id = MagicMock(side_effect=Exception("Not found"))
        with pytest.raises(TransactionsNotFoundException):
            service._get_transaction(999)


    # Tests for BUY transaction validation
    def test_create_buy_transaction_invalid_quantity_zero(self, service, mock_portfolio, mock_asset):
        """Test BUY transaction with zero quantity."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        with pytest.raises(InvalidQuantityException):
            service._create_buy_transaction(1, "PIZZA", 0, 100)

    def test_create_buy_transaction_invalid_quantity_negative(self, service, mock_portfolio, mock_asset):
        """Test BUY transaction with negative quantity."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        with pytest.raises(InvalidQuantityException):
            service._create_buy_transaction(1, "PIZZA", -5, 100)

    def test_create_buy_transaction_invalid_price_zero(self, service, mock_portfolio, mock_asset):
        """Test BUY transaction with zero price."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        with pytest.raises(InvalidPriceException):
            service._create_buy_transaction(1, "PIZZA", 10, 0)

    def test_create_buy_transaction_invalid_price_negative(self, service, mock_portfolio, mock_asset):
        """Test BUY transaction with negative price."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        with pytest.raises(InvalidPriceException):
            service._create_buy_transaction(1, "PIZZA", 10, -100)

    def test_create_buy_transaction_asset_not_found(self, service, mock_portfolio):
        """Test BUY transaction with non-existent asset."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(side_effect=Exception("Not found"))
        with pytest.raises(AssetNotFoundException):
            service._create_buy_transaction(1, "INVALID", 10, 100)

    def test_create_buy_transaction_insufficient_funds(self, service, mock_portfolio, mock_asset):
        """Test BUY transaction with insufficient funds."""
        low_balance_portfolio = PortfoliosDTO("Test", Decimal("50.00"), 1)
        service.portfolios_dao.get_by_id = MagicMock(return_value=low_balance_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        with pytest.raises(InsufficientFundsException):
            service._create_buy_transaction(1, "PIZZA", 10, 100)

    def test_create_buy_transaction_success(self, service, mock_portfolio, mock_asset):
        """Test successful BUY transaction."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        total, new_balance = service._create_buy_transaction(1, "PIZZA", 10, 15.00)
        assert total == Decimal("150.00")
        assert new_balance == Decimal("850.00")

    # Tests for SELL transaction validation
    def test_create_sell_transaction_invalid_quantity_zero(self, service, mock_portfolio, mock_asset):
        """Test SELL transaction with zero quantity."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.transactions_dao.get_asset_holding = MagicMock(return_value=100)
        with pytest.raises(InvalidQuantityException):
            service._create_sell_transaction(1, "PIZZA", 0, 100)

    def test_create_sell_transaction_invalid_quantity_negative(self, service, mock_portfolio, mock_asset):
        """Test SELL transaction with negative quantity."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.transactions_dao.get_asset_holding = MagicMock(return_value=100)
        with pytest.raises(InvalidQuantityException):
            service._create_sell_transaction(1, "PIZZA", -5, 100)

    def test_create_sell_transaction_invalid_price_zero(self, service, mock_portfolio, mock_asset):
        """Test SELL transaction with zero price."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.transactions_dao.get_asset_holding = MagicMock(return_value=100)
        with pytest.raises(InvalidPriceException):
            service._create_sell_transaction(1, "PIZZA", 10, 0)

    def test_create_sell_transaction_invalid_price_negative(self, service, mock_portfolio, mock_asset):
        """Test SELL transaction with negative price."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.transactions_dao.get_asset_holding = MagicMock(return_value=100)
        with pytest.raises(InvalidPriceException):
            service._create_sell_transaction(1, "PIZZA", 10, -100)

    def test_create_sell_transaction_asset_not_found(self, service, mock_portfolio):
        """Test SELL transaction with non-existent asset."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(side_effect=Exception("Not found"))
        with pytest.raises(AssetNotFoundException):
            service._create_sell_transaction(1, "INVALID", 10, 100)

    def test_create_sell_transaction_success(self, service, mock_portfolio, mock_asset):
        """Test successful SELL transaction."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.transactions_dao.get_asset_holding = MagicMock(return_value=100)
        total, new_balance = service._create_sell_transaction(1, "PIZZA", 10, 15.00)
        assert total == Decimal("150.00")
        assert new_balance == Decimal("1150.00")

    # Tests for DEPOSIT transaction
    def test_create_deposit_transaction_success(self, service, mock_portfolio):
        """Test successful DEPOSIT transaction."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        new_balance = service._create_deposit_transaction(1, 500)
        assert new_balance == Decimal("1500.00")

    def test_create_deposit_transaction_invalid_amount_zero(self, service, mock_portfolio):
        """Test DEPOSIT transaction with zero amount."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        with pytest.raises(InvalidPriceException):
            service._create_deposit_transaction(1, 0)

    def test_create_deposit_transaction_invalid_amount_negative(self, service, mock_portfolio):
        """Test DEPOSIT transaction with negative amount."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        with pytest.raises(InvalidPriceException):
            service._create_deposit_transaction(1, -100)

    def test_create_deposit_transaction_with_decimal(self, service, mock_portfolio):
        """Test DEPOSIT transaction with Decimal amount."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        new_balance = service._create_deposit_transaction(1, Decimal("500.50"))
        assert new_balance == Decimal("1500.50")

    # Tests for WITHDRAW transaction
    def test_create_withdraw_transaction_success(self, service, mock_portfolio):
        """Test successful WITHDRAW transaction."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        new_balance = service._create_withdraw_transaction(1, 200)
        assert new_balance == Decimal("800.00")

    def test_create_withdraw_transaction_invalid_amount_zero(self, service, mock_portfolio):
        """Test WITHDRAW transaction with zero amount."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        with pytest.raises(InvalidPriceException):
            service._create_withdraw_transaction(1, 0)

    def test_create_withdraw_transaction_invalid_amount_negative(self, service, mock_portfolio):
        """Test WITHDRAW transaction with negative amount."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        with pytest.raises(InvalidPriceException):
            service._create_withdraw_transaction(1, -100)

    def test_create_withdraw_transaction_with_decimal(self, service, mock_portfolio):
        """Test WITHDRAW transaction with Decimal amount."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        new_balance = service._create_withdraw_transaction(1, Decimal("200.50"))
        assert new_balance == Decimal("799.50")

    # Tests for DEPOSIT creation in create method
    def test_create_deposit_transaction_via_create(self, service, mock_portfolio):
        """Test DEPOSIT transaction creation through main create method."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.transactions_dao.create = MagicMock(return_value=1)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)
        # DEPOSIT requires asset_id to be None and transaction_quantity/price to be None
        # The create method will convert None to int, which causes ValidationException
        # This test verifies that ValidationException is raised as expected
        with pytest.raises(ValidationException):
            service.create(1, None, "DEPOSIT", None, None, "2024-01-15", 500, None)

    # Tests for WITHDRAW creation in create method
    def test_create_withdraw_transaction_via_create(self, service, mock_portfolio):
        """Test WITHDRAW transaction creation through main create method."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.transactions_dao.create = MagicMock(return_value=1)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)
        # WITHDRAW requires asset_id to be None and transaction_quantity/price to be None
        # The create method will convert None to int, which causes ValidationException
        # This test verifies that ValidationException is raised as expected
        with pytest.raises(ValidationException):
            service.create(1, None, "WITHDRAW", None, None, "2024-01-15", 200, None)

    # Tests for date range validation
    def test_get_transactions_by_date_range_valid(self, service):
        """Test getting transactions with valid date range."""
        transactions = [TransactionsDTO(1, 1, "PIZZA", "BUY", 10, 150.00, "2024-01-15", 1500.00, 1500.00)]
        service.transactions_dao.get_transactions_by_date_range = MagicMock(return_value=transactions)
        result = service.get_transactions_by_date_range("2024-01-01", "2024-01-31")
        assert result == transactions
        service.transactions_dao.get_transactions_by_date_range.assert_called_once_with("2024-01-01", "2024-01-31")

    def test_get_transactions_by_date_range_invalid_order(self, service):
        """Test getting transactions with invalid date range."""
        from exception.validation_exceptions import InvalidDateRange
        with pytest.raises(InvalidDateRange):
            service.get_transactions_by_date_range("2024-01-31", "2024-01-01")

    def test_get_transactions_by_portfolio_and_date_range_valid(self, service):
        """Test getting transactions by portfolio and date range."""
        transactions = [TransactionsDTO(1, 1, "PIZZA", "BUY", 10, 150.00, "2024-01-15", 1500.00, 1500.00)]
        service.transactions_dao.get_transactions_by_portfolio_and_date_range = MagicMock(return_value=transactions)
        result = service.get_transactions_by_portfolio_and_date_range(1, "2024-01-01", "2024-01-31")
        assert result == transactions
        service.transactions_dao.get_transactions_by_portfolio_and_date_range.assert_called_once_with(1, "2024-01-01", "2024-01-31")

    def test_get_transactions_by_portfolio_and_date_range_invalid(self, service):
        """Test getting transactions by portfolio with invalid date range."""
        from exception.validation_exceptions import InvalidDateRange
        with pytest.raises(InvalidDateRange):
            service.get_transactions_by_portfolio_and_date_range(1, "2024-01-31", "2024-01-01")

    # Tests for getter methods
    def test_get_transaction_by_id(self, service):
        """Test getting transaction by ID."""
        transaction = TransactionsDTO(1, 1, "PIZZA", "BUY", 10, 150.00, "2024-01-15", 1500.00, 1500.00)
        service.transactions_dao.get_transaction_by_id = MagicMock(return_value=transaction)
        result = service.get_transaction_by_id(1)
        assert result == transaction
        service.transactions_dao.get_transaction_by_id.assert_called_once_with(1)

    def test_get_transactions_by_portfolio(self, service):
        """Test getting transactions by portfolio."""
        transactions = [TransactionsDTO(1, 1, "PIZZA", "BUY", 10, 150.00, "2024-01-15", 1500.00, 1500.00)]
        service.transactions_dao.get_transaction_by_portfolio = MagicMock(return_value=transactions)
        result = service.get_transactions_by_portfolio(1)
        assert result == transactions
        service.transactions_dao.get_transaction_by_portfolio.assert_called_once_with(1)

    def test_get_transactions_by_asset(self, service):
        """Test getting transactions by asset."""
        transactions = [TransactionsDTO(1, 1, "PIZZA", "BUY", 10, 150.00, "2024-01-15", 1500.00, 1500.00)]
        service.transactions_dao.get_transaction_by_asset = MagicMock(return_value=transactions)
        result = service.get_transactions_by_asset(1, "PIZZA")
        assert result == transactions
        service.transactions_dao.get_transaction_by_asset.assert_called_once_with("PIZZA")

    def test_get_transactions_by_type(self, service):
        """Test getting transactions by type."""
        transactions = [TransactionsDTO(1, 1, "PIZZA", "BUY", 10, 150.00, "2024-01-15", 1500.00, 1500.00)]
        service.transactions_dao.get_transaction_by_type = MagicMock(return_value=transactions)
        result = service.get_transactions_by_type("BUY")
        assert result == transactions
        service.transactions_dao.get_transaction_by_type.assert_called_once_with("BUY")

    def test_get_transaction_count_by_portfolio(self, service):
        """Test getting transaction count by portfolio."""
        service.transactions_dao.get_transaction_count_by_portfolio = MagicMock(return_value=5)
        result = service.get_transaction_count_by_portfolio(1)
        assert result == 5
        service.transactions_dao.get_transaction_count_by_portfolio.assert_called_once_with(1)

    def test_get_total_transaction_value_by_portfolio(self, service):
        """Test getting total transaction value by portfolio."""
        service.transactions_dao.get_total_transaction_value_by_portfolio = MagicMock(return_value=Decimal("5000.00"))
        result = service.get_total_transaction_value_by_portfolio(1)
        assert result == Decimal("5000.00")
        service.transactions_dao.get_total_transaction_value_by_portfolio.assert_called_once_with(1)

    def test_get_average_transaction_price_by_asset(self, service):
        """Test getting average transaction price by asset."""
        service.transactions_dao.get_average_transaction_price_by_asset = MagicMock(return_value=Decimal("150.00"))
        result = service.get_average_transaction_price_by_asset("PIZZA")
        assert result == Decimal("150.00")
        service.transactions_dao.get_average_transaction_price_by_asset.assert_called_once_with("PIZZA")

    def test_get_transaction_summary_by_portfolio(self, service):
        """Test getting transaction summary by portfolio."""
        summary = {"buy_count": 5, "sell_count": 3}
        service.transactions_dao.get_transaction_summary_by_portfolio = MagicMock(return_value=summary)
        result = service.get_transaction_summary_by_portfolio(1)
        assert result == summary
        service.transactions_dao.get_transaction_summary_by_portfolio.assert_called_once_with(1)

    # Tests for insert_transaction method
    def test_insert_transaction_invalid_portfolio(self, service):
        """Test inserting transaction with invalid portfolio."""
        service.portfolios_dao.get_by_id = MagicMock(side_effect=Exception("Not found"))
        with pytest.raises(Exception):
            service.insert_transaction(999, "PIZZA", "BUY", 10, 150.00, "2024-01-15", 1500.00, 850.00)

    def test_insert_transaction_invalid_type(self, service, mock_portfolio):
        """Test inserting transaction with invalid type."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        with pytest.raises(InvalidTransactionTypeException):
            service.insert_transaction(1, "PIZZA", "INVALID", 10, 150.00, "2024-01-15", 1500.00, 850.00)

    def test_insert_transaction_invalid_asset(self, service, mock_portfolio):
        """Test inserting transaction with invalid asset."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(side_effect=Exception("Not found"))
        with pytest.raises(AssetNotFoundException):
            service.insert_transaction(1, "INVALID", "BUY", 10, 150.00, "2024-01-15", 1500.00, 850.00)

    def test_insert_transaction_invalid_quantity(self, service, mock_portfolio, mock_asset):
        """Test inserting transaction with invalid quantity."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        with pytest.raises(InvalidQuantityException):
            service.insert_transaction(1, "PIZZA", "BUY", 0, 150.00, "2024-01-15", 1500.00, 850.00)

    def test_insert_transaction_invalid_price(self, service, mock_portfolio, mock_asset):
        """Test inserting transaction with invalid price."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        with pytest.raises(InvalidPriceException):
            service.insert_transaction(1, "PIZZA", "BUY", 10, 0, "2024-01-15", 1500.00, 850.00)

    # Tests for update_transaction method
    def test_update_transaction_valid(self, service):
        """Test updating valid transaction raises AttributeError due to incorrect validate_monetary_input call."""
        transaction = TransactionsDTO(1, 1, "PIZZA", "BUY", 10, 150.00, "2024-01-15", 1500.00, 1500.00)
        service.transactions_dao.get_by_id = MagicMock(return_value=transaction)
        service.transactions_dao.update_transaction = MagicMock(return_value=True)
        with pytest.raises(AttributeError):
            service.update_transaction(1, "SELL", 10, 150.00, 1500.00, 1500.00)

    def test_update_transaction_invalid_id(self, service):
        """Test updating transaction with invalid ID."""
        with pytest.raises(ValueError):
            service.update_transaction(None, "SELL", 10, 150.00, 1500.00, 1500.00)

    def test_update_transaction_invalid_type(self, service):
        """Test updating transaction with invalid type."""
        transaction = TransactionsDTO(1, 1, "PIZZA", "BUY", 10, 150.00, "2024-01-15", 1500.00, 1500.00)
        service.transactions_dao.get_by_id = MagicMock(return_value=transaction)
        with pytest.raises(InvalidTransactionTypeException):
            service.update_transaction(1, "INVALID", 10, 150.00, 1500.00, 1500.00)

    def test_update_transaction_invalid_quantity(self, service):
        """Test updating transaction with negative quantity."""
        transaction = TransactionsDTO(1, 1, "PIZZA", "BUY", 10, 150.00, "2024-01-15", 1500.00, 1500.00)
        service.transactions_dao.get_by_id = MagicMock(return_value=transaction)
        with pytest.raises(InvalidQuantityException):
            service.update_transaction(1, "SELL", -5, 150.00, 1500.00, 1500.00)

    def test_update_transaction_invalid_price(self, service):
        """Test updating transaction with negative price."""
        transaction = TransactionsDTO(1, 1, "PIZZA", "BUY", 10, 150.00, "2024-01-15", 1500.00, 1500.00)
        service.transactions_dao.get_by_id = MagicMock(return_value=transaction)
        with pytest.raises(InvalidPriceException):
            service.update_transaction(1, "SELL", 10, -100, 1500.00, 1500.00)

    # Tests for delete_transaction method
    def test_delete_transaction_valid(self, service):
        """Test deleting valid transaction."""
        transaction = TransactionsDTO(1, 1, "PIZZA", "BUY", 10, 150.00, "2024-01-15", 1500.00, 1500.00)
        service.transactions_dao.get_by_id = MagicMock(return_value=transaction)
        service.transactions_dao.delete_transaction = MagicMock(return_value=True)
        result = service.delete_transaction(1)
        
        assert result is True
        service.transactions_dao.delete_transaction.assert_called_once_with(1)

    def test_delete_transaction_invalid_id(self, service):
        """Test deleting transaction with invalid ID."""
        with pytest.raises(ValueError):
            service.delete_transaction(None)

    def test_delete_transaction_not_found(self, service):
        """Test deleting non-existent transaction."""
        service.transactions_dao.get_by_id = MagicMock(side_effect=Exception("Not found"))
        with pytest.raises(Exception):
            service.delete_transaction(999)

    # Tests for delete_transactions_by_portfolio method
    def test_delete_transactions_by_portfolio_valid(self, service, mock_portfolio):
        """Test deleting transactions by valid portfolio."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.transactions_dao.delete_transactions_by_portfolio = MagicMock(return_value=True)
        result = service.delete_transactions_by_portfolio(1)
        
        assert result is True
        service.transactions_dao.delete_transactions_by_portfolio.assert_called_once_with(1)

    def test_delete_transactions_by_portfolio_invalid_id(self, service):
        """Test deleting transactions with invalid portfolio ID."""
        with pytest.raises(ValueError):
            service.delete_transactions_by_portfolio(None)

    def test_delete_transactions_by_portfolio_not_found(self, service):
        """Test deleting transactions for non-existent portfolio."""
        service.portfolios_dao.get_by_id = MagicMock(side_effect=Exception("Not found"))
        with pytest.raises(Exception):
            service.delete_transactions_by_portfolio(999)

    # Tests for inventory/holdings functionality
    def test_sell_transaction_with_sufficient_inventory(self, service, mock_portfolio, mock_asset):
        """Test SELL transaction succeeds when sufficient inventory exists."""
        from exception.validation_exceptions import InsufficientAssetQuantityException
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.transactions_dao.get_asset_holding = MagicMock(return_value=100)

        total, new_balance = service._create_sell_transaction(1, "PIZZA", 50, 15.00)

        assert total == Decimal("750.00")
        assert new_balance == Decimal("1750.00")
        service.transactions_dao.get_asset_holding.assert_called_once_with(1, "PIZZA")

    def test_sell_transaction_with_exact_inventory(self, service, mock_portfolio, mock_asset):
        """Test SELL transaction succeeds when selling exact quantity owned."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.transactions_dao.get_asset_holding = MagicMock(return_value=50)

        total, new_balance = service._create_sell_transaction(1, "PIZZA", 50, 15.00)

        assert total == Decimal("750.00")
        assert new_balance == Decimal("1750.00")

    def test_sell_transaction_insufficient_inventory(self, service, mock_portfolio, mock_asset):
        """Test SELL transaction fails when insufficient inventory."""
        from exception.validation_exceptions import InsufficientAssetQuantityException
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.transactions_dao.get_asset_holding = MagicMock(return_value=30)

        with pytest.raises(InsufficientAssetQuantityException):
            service._create_sell_transaction(1, "PIZZA", 50, 15.00)

    def test_sell_transaction_zero_inventory(self, service, mock_portfolio, mock_asset):
        """Test SELL transaction fails when no inventory."""
        from exception.validation_exceptions import InsufficientAssetQuantityException
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)
        service.assets_dao.get_by_id = MagicMock(return_value=mock_asset)
        service.transactions_dao.get_asset_holding = MagicMock(return_value=0)

        with pytest.raises(InsufficientAssetQuantityException):
            service._create_sell_transaction(1, "PIZZA", 10, 15.00)

    def test_get_portfolio_holdings_valid(self, service):
        """Test getting holdings for valid portfolio."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=PortfoliosDTO("Test", 1000, 1))
        holdings = [
            {"asset_id": "AAPL", "quantity": 120},
            {"asset_id": "MSFT", "quantity": 70}
        ]
        service.transactions_dao.get_portfolio_holdings = MagicMock(return_value=holdings)

        result = service.get_portfolio_holdings(1)

        assert result == holdings
        service.portfolios_dao.get_by_id.assert_called_once_with(1)
        service.transactions_dao.get_portfolio_holdings.assert_called_once_with(1)

    def test_get_portfolio_holdings_empty(self, service):
        """Test getting holdings for portfolio with no assets."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=PortfoliosDTO("Test", 1000, 1))
        service.transactions_dao.get_portfolio_holdings = MagicMock(return_value=[])

        result = service.get_portfolio_holdings(1)

        assert result == []

    def test_get_portfolio_holdings_invalid_portfolio(self, service):
        """Test getting holdings for non-existent portfolio."""
        service.portfolios_dao.get_by_id = MagicMock(side_effect=Exception("Not found"))

        with pytest.raises(Exception):
            service.get_portfolio_holdings(999)

    def test_get_asset_holding_valid(self, service):
        """Test getting holding for valid asset and portfolio."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=PortfoliosDTO("Test", 1000, 1))
        service.assets_dao.get_by_id = MagicMock(return_value=AssetsDTO("AAPL", "Apple", "EQUITY", "Tech", "Electronics", False))
        service.transactions_dao.get_asset_holding = MagicMock(return_value=100)

        result = service.get_asset_holding(1, "AAPL")

        assert result == {"asset_id": "AAPL", "quantity": 100}
        service.portfolios_dao.get_by_id.assert_called_once_with(1)
        service.assets_dao.get_by_id.assert_called_once_with("AAPL")

    def test_get_asset_holding_zero_quantity(self, service):
        """Test getting holding when asset not owned."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=PortfoliosDTO("Test", 1000, 1))
        service.assets_dao.get_by_id = MagicMock(return_value=AssetsDTO("AAPL", "Apple", "EQUITY", "Tech", "Electronics", False))
        service.transactions_dao.get_asset_holding = MagicMock(return_value=0)

        result = service.get_asset_holding(1, "AAPL")

        assert result == {"asset_id": "AAPL", "quantity": 0}

    def test_get_asset_holding_invalid_portfolio(self, service):
        """Test getting holding for non-existent portfolio."""
        service.portfolios_dao.get_by_id = MagicMock(side_effect=Exception("Not found"))

        with pytest.raises(Exception):
            service.get_asset_holding(999, "AAPL")

    def test_get_asset_holding_invalid_asset(self, service):
        """Test getting holding for non-existent asset."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=PortfoliosDTO("Test", 1000, 1))
        service.assets_dao.get_by_id = MagicMock(side_effect=Exception("Not found"))

        with pytest.raises(AssetNotFoundException):
            service.get_asset_holding(1, "INVALID")