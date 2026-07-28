class ValidationException(Exception):
    """Base exception for validation errors."""
    def __init__(self, message="Validation error occurred"):
        self.message = message
        super().__init__(self.message)


class InsufficientFundsException(ValidationException):
    """Raised when portfolio doesn't have enough balance for a transaction."""
    def __init__(self, required, available):
        self.required = required
        self.available = available
        message = f"Insufficient funds! You need ${required:.2f} but only have ${available:.2f} in your account."
        super().__init__(message)


class InvalidQuantityException(ValidationException):
    """Raised when transaction quantity is invalid."""
    def __init__(self, quantity=None):
        if quantity is None:
            message = "Quantity must be a positive number greater than zero."
        else:
            message = f"Invalid quantity: {quantity}. Quantity must be a positive number."
        super().__init__(message)


class InvalidPriceException(ValidationException):
    """Raised when transaction price is invalid."""
    def __init__(self, price=None):
        if price is None:
            message = "Price must be a positive number greater than zero."
        else:
            message = f"Invalid price: ${price}. Price must be a positive number."
        super().__init__(message)


class PortfolioNotFoundException(ValidationException):
    """Raised when portfolio doesn't exist."""
    def __init__(self, portfolio_id=None):
        if portfolio_id is None:
            message = "Portfolio not found. Please check the portfolio ID and try again."
        else:
            message = f"Portfolio with ID {portfolio_id} not found. The portfolio does not exist in the system."
        super().__init__(message)


class AssetNotFoundException(ValidationException):
    """Raised when asset doesn't exist."""
    def __init__(self, asset_id=None):
        if asset_id is None:
            message = "Asset not found. Please check the asset ID and try again."
        else:
            message = f"Asset with ID '{asset_id}' not found. This asset does not exist in the system."
        super().__init__(message)


class InvalidTransactionTypeException(ValidationException):
    """Raised when transaction type is invalid."""
    def __init__(self, transaction_type=None, valid_types=None):
        if valid_types is None:
            valid_types = ["BUY", "SELL"]

        if transaction_type is None:
            message = f"Invalid transaction type. Valid types are: {', '.join(valid_types)}"
        else:
            message = f"Invalid transaction type '{transaction_type}'. Valid types are: {', '.join(valid_types)}"
        super().__init__(message)
