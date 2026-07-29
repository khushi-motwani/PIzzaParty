import logging
from dao.portfolios_dao import PortfoliosDao
from exception.validation_exceptions import (
    InvalidPortfolioNameException,
    InvalidAmountException,
    InsufficientFundsException
)

logger = logging.getLogger('pizzaparty')

class PortfoliosService:
    def __init__(self):
        logger.debug("Initializing PortfoliosService")
        self.portfolios_dao = PortfoliosDao()

    def _validate_portfolio_id(self, portfolio_id):
        """Validate that portfolio ID is valid and portfolio exists."""
        if portfolio_id is None or portfolio_id <= 0:
            logger.critical(f"Invalid portfolio ID: {portfolio_id}")
            raise ValueError("Portfolio ID must be a positive integer.")
        try:
            self.portfolios_dao.get_by_id(portfolio_id)
        except Exception:
            logger.critical(f"Portfolio not found: {portfolio_id}")
            raise

    def _validate_portfolio_name(self, name):
        """Validate that portfolio name is non-empty string."""
        if name is None or not isinstance(name, str) or name.strip() == "":
            logger.critical(f"Invalid portfolio name: {name}")
            raise InvalidPortfolioNameException(name)
        if len(name) > 255:
            logger.critical(f"Portfolio name exceeds maximum length: {name}")
            raise InvalidPortfolioNameException(name)

    def _validate_balance(self, balance):
        """Validate that balance is a non-negative number."""
        if balance is None or not isinstance(balance, (int, float)):
            logger.critical(f"Invalid balance type: {balance}")
            raise ValueError("Balance must be a valid number.")
        if balance < 0:
            logger.critical(f"Negative balance not allowed: {balance}")
            raise ValueError("Balance cannot be negative.")

    def _validate_amount(self, amount):
        """Validate that amount is a positive number."""
        if amount is None or not isinstance(amount, (int, float)):
            logger.critical(f"Invalid amount type: {amount}")
            raise InvalidAmountException(amount)
        if amount <= 0:
            logger.critical(f"Invalid amount value (must be positive): {amount}")
            raise InvalidAmountException(amount)

    def _check_sufficient_funds(self, portfolio_id, amount):
        """Check if portfolio has sufficient funds for the operation."""
        portfolio = self.portfolios_dao.get_portfolio_balance(portfolio_id)
        if portfolio.portfolio_balance < amount:
            logger.critical(f"Insufficient funds: portfolio_id={portfolio_id}, required=${amount}, available=${portfolio.portfolio_balance}")
            raise InsufficientFundsException(amount, portfolio.portfolio_balance)

    def get_all(self):
        logger.debug("Retrieving all portfolios")
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
        logger.debug("Counting total portfolios")
        return self.portfolios_dao.count()

    def get_sorted_by_balance_desc(self):
        return self.portfolios_dao.get_sorted_by_balance_desc()

    def get_sorted_by_balance_asc(self):
        return self.portfolios_dao.get_sorted_by_balance_asc()

    def create(self, portfolio_name, portfolio_balance=0):
        self._validate_portfolio_name(portfolio_name)
        self._validate_balance(portfolio_balance)
        portfolio_id = self.portfolios_dao.create(portfolio_name, portfolio_balance)
        logger.info(f"Portfolio created: ID={portfolio_id}, name={portfolio_name}, initial_balance=${portfolio_balance}")
        return portfolio_id

    def update_name(self, portfolio_id, portfolio_name):
        self._validate_portfolio_id(portfolio_id)
        self._validate_portfolio_name(portfolio_name)
        logger.info(f"Portfolio name updated: portfolio_id={portfolio_id}, new_name={portfolio_name}")
        return self.portfolios_dao.update_name(portfolio_id, portfolio_name)

    def update_balance(self, portfolio_id, new_balance):
        self._validate_portfolio_id(portfolio_id)
        self._validate_balance(new_balance)
        logger.info(f"Portfolio balance updated: portfolio_id={portfolio_id}, new_balance=${new_balance}")
        return self.portfolios_dao.update_balance(portfolio_id, new_balance)

    def increment_balance(self, portfolio_id, amount):
        self._validate_portfolio_id(portfolio_id)
        self._validate_amount(amount)
        logger.info(f"Portfolio balance incremented: portfolio_id={portfolio_id}, amount=${amount}")
        return self.portfolios_dao.increment_balance(portfolio_id, amount)

    def decrement_balance(self, portfolio_id, amount):
        self._validate_portfolio_id(portfolio_id)
        self._validate_amount(amount)
        self._check_sufficient_funds(portfolio_id, amount)
        logger.info(f"Portfolio balance decremented: portfolio_id={portfolio_id}, amount=${amount}")
        return self.portfolios_dao.decrement_balance(portfolio_id, amount)

    def delete(self, portfolio_id):
        self._validate_portfolio_id(portfolio_id)
        logger.info(f"Portfolio deleted: portfolio_id={portfolio_id}")
        return self.portfolios_dao.delete(portfolio_id)
