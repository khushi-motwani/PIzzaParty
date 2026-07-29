from dao.portfolios_dao import PortfoliosDao
from exception.validation_exceptions import (
    InvalidPortfolioNameException,
    InvalidAmountException,
    InsufficientFundsException
)

class PortfoliosService:
    def __init__(self):
        self.portfolios_dao = PortfoliosDao()

    def _validate_portfolio_id(self, portfolio_id):
        """Validate that portfolio ID is valid and portfolio exists."""
        if portfolio_id is None or portfolio_id <= 0:
            raise ValueError("Portfolio ID must be a positive integer.")
        self.portfolios_dao.get_by_id(portfolio_id)

    def _validate_portfolio_name(self, name):
        """Validate that portfolio name is non-empty string."""
        if name is None or not isinstance(name, str) or name.strip() == "":
            raise InvalidPortfolioNameException(name)
        if len(name) > 255:
            raise InvalidPortfolioNameException(name)

    def _validate_balance(self, balance):
        """Validate that balance is a non-negative number."""
        if balance is None or not isinstance(balance, (int, float)):
            raise ValueError("Balance must be a valid number.")
        if balance < 0:
            raise ValueError("Balance cannot be negative.")

    def _validate_amount(self, amount):
        """Validate that amount is a positive number."""
        if amount is None or not isinstance(amount, (int, float)):
            raise InvalidAmountException(amount)
        if amount <= 0:
            raise InvalidAmountException(amount)

    def _check_sufficient_funds(self, portfolio_id, amount):
        """Check if portfolio has sufficient funds for the operation."""
        portfolio = self.portfolios_dao.get_portfolio_balance(portfolio_id)
        if portfolio.portfolio_balance < amount:
            raise InsufficientFundsException(amount, portfolio.portfolio_balance)

    def get_all(self):
        return self.portfolios_dao.get_all()

    def get_by_id(self, portfolio_id):
        return self.portfolios_dao.get_by_id(portfolio_id)

    def get_portfolio_balance(self, portfolio_id):
        return self.portfolios_dao.get_portfolio_balance(portfolio_id)

    def get_total_balance(self):
        return self.portfolios_dao.get_total_balance()

    def get_count(self):
        return self.portfolios_dao.get_count()

    def count(self):
        return self.portfolios_dao.count()

    def get_sorted_by_balance_desc(self):
        return self.portfolios_dao.get_sorted_by_balance_desc()

    def get_sorted_by_balance_asc(self):
        return self.portfolios_dao.get_sorted_by_balance_asc()

    def create(self, portfolio_name, portfolio_balance=0):
        self._validate_portfolio_name(portfolio_name)
        self._validate_balance(portfolio_balance)
        return self.portfolios_dao.create(portfolio_name, portfolio_balance)

    def update_name(self, portfolio_id, portfolio_name):
        self._validate_portfolio_id(portfolio_id)
        self._validate_portfolio_name(portfolio_name)
        return self.portfolios_dao.update_name(portfolio_id, portfolio_name)

    def update_balance(self, portfolio_id, new_balance):
        self._validate_portfolio_id(portfolio_id)
        self._validate_balance(new_balance)
        return self.portfolios_dao.update_balance(portfolio_id, new_balance)

    def increment_balance(self, portfolio_id, amount):
        self._validate_portfolio_id(portfolio_id)
        self._validate_amount(amount)
        return self.portfolios_dao.increment_balance(portfolio_id, amount)

    def decrement_balance(self, portfolio_id, amount):
        self._validate_portfolio_id(portfolio_id)
        self._validate_amount(amount)
        self._check_sufficient_funds(portfolio_id, amount)
        return self.portfolios_dao.decrement_balance(portfolio_id, amount)

    def delete(self, portfolio_id):
        self._validate_portfolio_id(portfolio_id)
        return self.portfolios_dao.delete(portfolio_id)
