import logging
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

logger = logging.getLogger('pizzaparty')

class TransactionsService:
    VALID_TRANSACTION_TYPES = ["BUY", "SELL"]

    def __init__(self):
        self.transactions_dao = TransactionsDao()
        self.portfolios_dao = PortfoliosDao()
        self.assets_dao = AssetsDao()

    def get_all(self):
        logger.debug("Retrieving all transactions")
        return self.transactions_dao.get_all()

    def count(self):
        logger.debug("Counting total transactions")
        return self.transactions_dao.count()

    def create_transaction(self, portfolio_id, asset_id, transaction_type, quantity, price):
        logger.info(f"Creating {transaction_type} transaction: portfolio_id={portfolio_id}, asset_id={asset_id}, quantity={quantity}, price={price}")
        try:
            # Validate transaction type
            if transaction_type not in self.VALID_TRANSACTION_TYPES:
                logger.warning(f"Invalid transaction type attempted: {transaction_type}")
                raise InvalidTransactionTypeException(transaction_type, self.VALID_TRANSACTION_TYPES)

            # Validate quantity
            if not isinstance(quantity, (int, float)) or quantity <= 0:
                logger.warning(f"Invalid quantity attempted: {quantity}")
                raise InvalidQuantityException(quantity)

            # Validate price
            if not isinstance(price, (int, float, Decimal)) or price <= 0:
                logger.warning(f"Invalid price attempted: {price}")
                raise InvalidPriceException(price)

            # Get portfolio and validate it exists
            try:
                portfolio = self.portfolios_dao.get_by_id(portfolio_id)
                logger.debug(f"Portfolio retrieved: ID={portfolio_id}, balance=${portfolio.portfolio_balance}")
            except Exception as e:
                logger.error(f"Portfolio not found: {portfolio_id}", exc_info=True)
                raise PortfolioNotFoundException(portfolio_id) from e

            # Validate asset exists
            try:
                self.assets_dao.get_by_id(asset_id)
                logger.debug(f"Asset validated: {asset_id}")
            except Exception as e:
                logger.error(f"Asset not found: {asset_id}", exc_info=True)
                raise AssetNotFoundException(asset_id) from e

            # Calculate transaction total
            transaction_total = Decimal(str(quantity)) * Decimal(str(price))
            logger.debug(f"Transaction total calculated: ${transaction_total}")

            # For BUY transactions, check sufficient funds
            if transaction_type == "BUY":
                logger.info(f"Processing BUY order: asset_id={asset_id}, quantity={quantity}, price=${price}, total=${transaction_total}")
                if portfolio.portfolio_balance < transaction_total:
                    logger.warning(f"Insufficient funds for BUY: required=${transaction_total}, available=${portfolio.portfolio_balance}")
                    raise InsufficientFundsException(float(transaction_total), float(portfolio.portfolio_balance))
                new_balance = portfolio.portfolio_balance - transaction_total
                logger.debug(f"BUY validated: new_balance will be ${new_balance}")
            else:  # SELL
                logger.info(f"Processing SELL order: asset_id={asset_id}, quantity={quantity}, price=${price}, total=${transaction_total}")
                new_balance = portfolio.portfolio_balance + transaction_total
                logger.debug(f"SELL processed: new_balance will be ${new_balance}")

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
                logger.info(f"Transaction successfully created: ID={transaction_id}, type={transaction_type}")
            except Exception as e:
                logger.critical(f"Failed to create transaction in database: {str(e)}", exc_info=True)
                raise ValidationException("Failed to create transaction in database") from e

            # Update portfolio balance
            try:
                self.portfolios_dao.update_balance(portfolio_id, new_balance)
                logger.info(f"Portfolio balance updated: portfolio_id={portfolio_id}, new_balance=${new_balance}")
            except Exception as e:
                logger.critical(f"Failed to update portfolio balance: {str(e)}", exc_info=True)
                raise ValidationException("Failed to update portfolio balance") from e

            logger.info(f"Transaction completed successfully: ID={transaction_id}, type={transaction_type}, portfolio_id={portfolio_id}")
            return transaction_id

        except (InvalidTransactionTypeException, InvalidQuantityException, InvalidPriceException,
                PortfolioNotFoundException, AssetNotFoundException, InsufficientFundsException) as e:
            logger.critical(f"Validation exception during transaction: {str(e)}", exc_info=True)
            raise
        except ValidationException as e:
            logger.critical(f"Validation error during transaction: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.critical(f"Unexpected error during transaction creation: {str(e)}", exc_info=True)
            raise ValidationException(f"Unexpected error during transaction creation: {str(e)}") from e
