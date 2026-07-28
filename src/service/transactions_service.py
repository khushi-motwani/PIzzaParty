from decimal import Decimal
from datetime import datetime
from dao.transactions_dao import TransactionsDao
from dao.portfolios_dao import PortfoliosDao
from dao.assets_dao import AssetsDao
from exception.validation_exceptions import (
    ValidationException,
    InsufficientFundsException,
    InvalidQuantityException,
    InvalidPriceException,
    InvalidTransactionTypeException,
    PortfolioNotFoundException,
    AssetNotFoundException
)

class TransactionsService:
    VALID_TRANSACTION_TYPES = ["BUY", "SELL"]

    def __init__(self):
        self.transactions_dao = TransactionsDao()
        self.portfolios_dao = PortfoliosDao()
        self.assets_dao = AssetsDao()

    def get_all(self):
        return self.transactions_dao.get_all()

    def count(self):
        return self.transactions_dao.count()

    def create_transaction(self, portfolio_id, asset_id, transaction_type, quantity, price):
        try:
            # Validate transaction type
            if transaction_type not in self.VALID_TRANSACTION_TYPES:
                raise InvalidTransactionTypeException(transaction_type, self.VALID_TRANSACTION_TYPES)

            # Validate quantity
            if not isinstance(quantity, (int, float)) or quantity <= 0:
                raise InvalidQuantityException(quantity)

            # Validate price
            if not isinstance(price, (int, float, Decimal)) or price <= 0:
                raise InvalidPriceException(price)

            # Get portfolio and validate it exists
            try:
                portfolio = self.portfolios_dao.get_by_id(portfolio_id)
            except Exception as e:
                raise PortfolioNotFoundException(portfolio_id) from e

            # Validate asset exists
            try:
                self.assets_dao.get_by_id(asset_id)
            except Exception as e:
                raise AssetNotFoundException(asset_id) from e

            # Calculate transaction total
            transaction_total = Decimal(str(quantity)) * Decimal(str(price))

            # For BUY transactions, check sufficient funds
            if transaction_type == "BUY":
                if portfolio.portfolio_balance < transaction_total:
                    raise InsufficientFundsException(float(transaction_total), float(portfolio.portfolio_balance))
                new_balance = portfolio.portfolio_balance - transaction_total
            else:  # SELL
                new_balance = portfolio.portfolio_balance + transaction_total

            # Create the transaction
            transaction_date = datetime.now()
            try:
                transaction_id = self.transactions_dao.create(
                    portfolio_id=portfolio_id,
                    asset_id=asset_id,
                    transaction_type=transaction_type,
                    transaction_quantity=int(quantity),
                    transaction_price=Decimal(str(price)),
                    transaction_date=transaction_date,
                    transaction_total=transaction_total,
                    balance_after_transaction=new_balance
                )
            except Exception as e:
                raise ValidationException("Failed to create transaction in database") from e

            # Update portfolio balance
            try:
                self.portfolios_dao.update_balance(portfolio_id, new_balance)
            except Exception as e:
                raise ValidationException("Failed to update portfolio balance") from e

            return transaction_id

        except (InvalidTransactionTypeException, InvalidQuantityException, InvalidPriceException,
                PortfolioNotFoundException, AssetNotFoundException, InsufficientFundsException):
            raise
        except ValidationException:
            raise
        except Exception as e:
            raise ValidationException(f"Unexpected error during transaction creation: {str(e)}") from e
