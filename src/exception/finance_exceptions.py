class FinanceException(Exception):
    """Base exception for finance-related errors."""
    def __init__(self, message="Finance error occurred"):
        self.message = message
        super().__init__(self.message)


class TickerNotFoundError(FinanceException):
    """Raised when a ticker symbol cannot be found or has no price data."""
    def __init__(self, ticker=None):
        if ticker is None:
            message = "Ticker not found. Please check the ticker symbol and try again."
        else:
            message = f"Ticker '{ticker}' not found. No data available for this symbol."
        super().__init__(message)


class FinanceApiError(FinanceException):
    """Raised when the finance API fails or is unavailable."""
    def __init__(self, ticker=None, source=None):
        if ticker is None:
            message = "Finance API error. Unable to fetch data at this time."
        elif source is None:
            message = f"Failed to fetch quote for '{ticker}'. Please try again later."
        else:
            message = f"Failed to fetch quote for '{ticker}' from {source}. Please try again later."
        super().__init__(message)
