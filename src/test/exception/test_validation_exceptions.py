import pytest
from exception.validation_exceptions import (
    ValidationException,
    InsufficientFundsException,
    InvalidQuantityException,
    InvalidPriceException,
    PortfolioNotFoundException,
    AssetNotFoundException,
    InvalidTransactionTypeException
)


class TestValidationExceptions:
    """Test custom validation exceptions."""

    def test_validation_exception_with_message(self):
        """Test ValidationException with custom message."""
        exc = ValidationException("Custom error message")
        assert str(exc) == "Custom error message"

    def test_validation_exception_default_message(self):
        """Test ValidationException with default message."""
        exc = ValidationException()
        assert str(exc) == "Validation error occurred"

    def test_insufficient_funds_exception_formatting(self):
        """Test InsufficientFundsException formats numbers correctly."""
        exc = InsufficientFundsException(62.50, 50.00)
        error_msg = str(exc)

        assert "Insufficient funds" in error_msg
        assert "$62.50" in error_msg
        assert "$50.00" in error_msg

    def test_insufficient_funds_exception_with_decimals(self):
        """Test InsufficientFundsException with decimal values."""
        exc = InsufficientFundsException(100.99, 50.49)
        error_msg = str(exc)

        assert "$100.99" in error_msg
        assert "$50.49" in error_msg

    def test_invalid_quantity_exception_without_quantity(self):
        """Test InvalidQuantityException without quantity parameter."""
        exc = InvalidQuantityException()
        error_msg = str(exc)

        assert "Quantity must be a positive number greater than zero" in error_msg

    def test_invalid_quantity_exception_with_negative_quantity(self):
        """Test InvalidQuantityException with negative quantity."""
        exc = InvalidQuantityException(-5)
        error_msg = str(exc)

        assert "Invalid quantity: -5" in error_msg

    def test_invalid_quantity_exception_with_zero_quantity(self):
        """Test InvalidQuantityException with zero quantity."""
        exc = InvalidQuantityException(0)
        error_msg = str(exc)

        assert "Invalid quantity: 0" in error_msg

    def test_invalid_price_exception_without_price(self):
        """Test InvalidPriceException without price parameter."""
        exc = InvalidPriceException()
        error_msg = str(exc)

        assert "Price must be a positive number greater than zero" in error_msg

    def test_invalid_price_exception_with_negative_price(self):
        """Test InvalidPriceException with negative price."""
        exc = InvalidPriceException(-10.50)
        error_msg = str(exc)

        assert "Invalid price: $-10.5" in error_msg

    def test_invalid_price_exception_with_zero_price(self):
        """Test InvalidPriceException with zero price."""
        exc = InvalidPriceException(0)
        error_msg = str(exc)

        assert "Invalid price: $0" in error_msg

    def test_portfolio_not_found_exception_without_id(self):
        """Test PortfolioNotFoundException without ID parameter."""
        exc = PortfolioNotFoundException()
        error_msg = str(exc)

        assert "Portfolio not found" in error_msg
        assert "check the portfolio ID" in error_msg

    def test_portfolio_not_found_exception_with_id(self):
        """Test PortfolioNotFoundException with portfolio ID."""
        exc = PortfolioNotFoundException(999)
        error_msg = str(exc)

        assert "Portfolio with ID 999 not found" in error_msg
        assert "does not exist in the system" in error_msg

    def test_asset_not_found_exception_without_id(self):
        """Test AssetNotFoundException without ID parameter."""
        exc = AssetNotFoundException()
        error_msg = str(exc)

        assert "Asset not found" in error_msg
        assert "check the asset ID" in error_msg

    def test_asset_not_found_exception_with_id(self):
        """Test AssetNotFoundException with asset ID."""
        exc = AssetNotFoundException("PIZZA001")
        error_msg = str(exc)

        assert "Asset with ID 'PIZZA001' not found" in error_msg
        assert "does not exist in the system" in error_msg

    def test_invalid_transaction_type_exception_without_type(self):
        """Test InvalidTransactionTypeException without type parameter."""
        exc = InvalidTransactionTypeException()
        error_msg = str(exc)

        assert "Invalid transaction type" in error_msg
        assert "BUY, SELL" in error_msg

    def test_invalid_transaction_type_exception_with_type(self):
        """Test InvalidTransactionTypeException with transaction type."""
        exc = InvalidTransactionTypeException("TRADE")
        error_msg = str(exc)

        assert "Invalid transaction type 'TRADE'" in error_msg
        assert "BUY, SELL" in error_msg

    def test_invalid_transaction_type_exception_with_custom_types(self):
        """Test InvalidTransactionTypeException with custom valid types."""
        valid_types = ["CREATE", "DELETE", "UPDATE"]
        exc = InvalidTransactionTypeException("INVALID", valid_types)
        error_msg = str(exc)

        assert "Invalid transaction type 'INVALID'" in error_msg
        assert "CREATE, DELETE, UPDATE" in error_msg

    def test_exception_inheritance(self):
        """Test that all custom exceptions inherit from ValidationException."""
        exceptions = [
            InsufficientFundsException(100, 50),
            InvalidQuantityException(-5),
            InvalidPriceException(-10),
            PortfolioNotFoundException(1),
            AssetNotFoundException("PIZZA"),
            InvalidTransactionTypeException("TRADE")
        ]

        for exc in exceptions:
            assert isinstance(exc, ValidationException)

    def test_exception_is_raisable(self):
        """Test that exceptions can be raised and caught."""
        with pytest.raises(InsufficientFundsException):
            raise InsufficientFundsException(100, 50)

        with pytest.raises(InvalidQuantityException):
            raise InvalidQuantityException(-5)

        with pytest.raises(InvalidPriceException):
            raise InvalidPriceException(-10)

        with pytest.raises(PortfolioNotFoundException):
            raise PortfolioNotFoundException(999)

        with pytest.raises(AssetNotFoundException):
            raise AssetNotFoundException("INVALID")

        with pytest.raises(InvalidTransactionTypeException):
            raise InvalidTransactionTypeException("TRADE")
