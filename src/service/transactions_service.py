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
    TransactionsNotFoundException,
    InvalidDateRange,
    PortfolioNotFoundException,
    AssetNotFoundException,
    InsufficientAssetQuantityException
)

logger = logging.getLogger('pizzaparty')

class TransactionsService:
    VALID_TRANSACTION_TYPES = ["BUY", "SELL", "DEPOSIT", "WITHDRAW"]

    def __init__(self):
        self.transactions_dao = TransactionsDao()
        self.portfolios_dao = PortfoliosDao()
        self.assets_dao = AssetsDao()
    
    def _get_transaction(self, transaction_id):
        try:
            logger.debug(f"Transaction retrieved: ID={transaction_id}")
            return self.transactions_dao.get_by_id(transaction_id)
        except Exception as e:
            raise TransactionsNotFoundException(transaction_id) from e
   
    def _validate_transaction_id(self, transaction_id):
            """Validate that transaction ID is valid and transaction exists."""
            if transaction_id is None or transaction_id <= 0:
                logger.critical(f"Invalid transaction ID: {transaction_id}")
                raise ValueError("Transaction ID must be a positive integer.")
            try:
                self.transactions_dao.get_by_id(transaction_id)
            except Exception:
                logger.critical(f"Transaction not found: {transaction_id}")
                raise
            
    def _validate_transaction_type(self, transaction_type):
        if transaction_type not in self.VALID_TRANSACTION_TYPES:
                logger.warning(f"Invalid transaction type attempted: {transaction_type}")
                raise InvalidTransactionTypeException(transaction_type, self.VALID_TRANSACTION_TYPES)
                
    def _get_portfolio(self, portfolio_id):
            try:
                portfolio = self.portfolios_dao.get_by_id(portfolio_id)
                logger.debug(f"Portfolio retrieved: ID={portfolio_id}")
                return portfolio
            except Exception as e:
                raise PortfolioNotFoundException(portfolio_id) from e
            
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
        
    # validate monetary values to reuse for balance_after_transaction, transaction_price and transaction_total
    def _validate_monetary_input(self, value):
        if value is None or not isinstance(value, (int, float, Decimal)):
            logger.critical(f"Invalid balance type: {value}")
            raise ValueError(f"{value} must be a valid number: {value}")
        if value < 0:
            logger.critical(f"Negative {value} not allowed: {value}")
            raise ValueError(f"{value} cannot be negative.")
    
    def get_all(self):
        logger.debug("Retrieving all transactions")
        return self.transactions_dao.get_all()
    
    def count(self):
        logger.debug("Counting total transactions")
        return self.transactions_dao.count()
    
    def create(self, portfolio_id, asset_id, transaction_type, transaction_quantity,
               transaction_price, transaction_date, transaction_total, balance_after_transaction):
        
        if transaction_type == "BUY":
            transaction_total, balance_after_transaction = self._create_buy_transaction(portfolio_id, asset_id, transaction_quantity, transaction_price);
        elif transaction_type == "SELL":
            transaction_total, balance_after_transaction = self._create_sell_transaction(portfolio_id, asset_id, transaction_quantity, transaction_price);
        elif transaction_type == "DEPOSIT":
            balance_after_transaction = self._create_deposit_transaction(portfolio_id, transaction_total);    
        elif transaction_type == "WITHDRAW": 
            balance_after_transaction = self._create_withdraw_transaction(portfolio_id, transaction_total);
        else:
            raise(InvalidTransactionTypeException)
        
        # timestamp
        transaction_date = datetime.now()

        try:
            balance_decimal = Decimal(str(balance_after_transaction)) if balance_after_transaction is not None else Decimal('0')

            transaction_id = self.transactions_dao.create(
                portfolio_id = portfolio_id,
                asset_id = asset_id,
                transaction_type = transaction_type,
                transaction_quantity = int(transaction_quantity) if transaction_quantity is not None else 0,
                transaction_price = Decimal(str(transaction_price)) if transaction_price is not None else Decimal('0'),
                transaction_date=  transaction_date,
                transaction_total = Decimal(str(transaction_total)) if transaction_total is not None else Decimal('0'),
                balance_after_transaction = balance_decimal)

            self.portfolios_dao.update_balance(portfolio_id, balance_decimal)
            
            logger.info(f"Transaction successfully created: ID={transaction_id}, type={transaction_type} at {transaction_date}")
        except Exception as e:
            raise ValidationException("Failed to create transaction in database") from e
        return transaction_id
        
    def _create_buy_transaction(self, portfolio_id, asset_id, quantity, price):
        logger.info(f"Creating BUY transaction: portfolio={portfolio_id}, asset={asset_id}")

        # Validate quantity
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            raise InvalidQuantityException(quantity)

        # Validate price
        if not isinstance(price, (int, float, Decimal)) or price <= 0:
            raise InvalidPriceException(price)
        
        # Validate asset exists
        try:
            self.assets_dao.get_by_id(asset_id)
            logger.debug(f"Asset validated: {asset_id}")
        except Exception as e:
            raise AssetNotFoundException(asset_id) from e
        
        # Calculate transaction total
        transaction_total = Decimal(str(quantity)) * Decimal(str(price))
        logger.debug(f"Transaction total calculated: ${transaction_total}")
        
        logger.info(f"Processing BUY order: asset_id={asset_id}, quantity={quantity}, price=${price}, total=${transaction_total}")
        
        # Check sufficient funds in portfolio for transactionv#
        portfolio = self._get_portfolio(portfolio_id)
        if portfolio.portfolio_balance < transaction_total:
            logger.warning(f"Insufficient funds in portfolio for BUY: required=${transaction_total}, available=${portfolio.portfolio_balance}")
            raise InsufficientFundsException(float(transaction_total), float(portfolio.portfolio_balance))
        
        new_balance = Decimal(str(portfolio.portfolio_balance)) - Decimal(str(transaction_total))
        logger.debug(f"BUY validated: new_balance will be ${new_balance}")
    
        return (transaction_total, new_balance)
    
    def _create_sell_transaction(self, portfolio_id, asset_id, quantity, price):
        logger.info(f"Creating SELL transaction: portfolio={portfolio_id}, asset={asset_id}")

        # Validate quantity
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            raise InvalidQuantityException(quantity)

        # Validate price
        if not isinstance(price, (int, float, Decimal)) or price <= 0:
            raise InvalidPriceException(price)

        # Validate asset exists
        try:
            self.assets_dao.get_by_id(asset_id)
            logger.debug(f"Asset validated: {asset_id}")
        except Exception as e:
            raise AssetNotFoundException(asset_id) from e

        # Check inventory - verify portfolio owns enough of this asset
        quantity_held = self.transactions_dao.get_asset_holding(portfolio_id, asset_id)
        if quantity_held < quantity:
            logger.warning(f"Insufficient asset quantity for SELL: asset={asset_id}, required={quantity}, available={quantity_held}")
            raise InsufficientAssetQuantityException(asset_id, int(quantity), int(quantity_held))

        # Calculate transaction total
        transaction_total = Decimal(str(quantity)) * Decimal(str(price))
        logger.debug(f"Transaction total calculated: ${transaction_total}")

        logger.info(f"Processing SELL order: asset_id={asset_id}, quantity={quantity}, price=${price}, total=${transaction_total}")

        portfolio = self._get_portfolio(portfolio_id)
        new_balance = Decimal(str(portfolio.portfolio_balance)) + Decimal(str(transaction_total))
        logger.debug(f"SELL validated: new_balance will be ${new_balance}")

        return (transaction_total, new_balance)
    
    def _create_deposit_transaction(self, portfolio_id, amount):
        logger.info(f"Creating DEPOSIT transaction: portfolio={portfolio_id}, amount={amount}")
        
        # amount = Decimal(str(amount))
                
        if not isinstance(amount, (int, float, Decimal)) or amount <= 0:
            logger.warning(f"Invalid amount attempted for DEPOSIT: {amount}")
            raise InvalidPriceException(amount)
                        
        portfolio = self._get_portfolio(portfolio_id)
        new_balance = Decimal(str(portfolio.portfolio_balance)) + Decimal(str(amount))
        logger.debug(f"DEPOSIT validated: new_balance will be ${new_balance}")
        
        return new_balance
        
    def _create_withdraw_transaction(self, portfolio_id, amount):
        logger.info(f"Creating WITHDRAW transaction: portfolio={portfolio_id}")

        # amount = Decimal(str(amount))
        # Check sufficient funds
        if not isinstance(amount, (int, float, Decimal)) or amount <= 0:
            logger.warning(f"Invalid amount attempted for WITHDRAW: {amount}")
            raise InvalidPriceException(amount)

        portfolio = self._get_portfolio(portfolio_id)
        new_balance = Decimal(str(portfolio.portfolio_balance)) - Decimal(str(amount))

        if new_balance < 0:
            logger.warning(f"Insufficient funds for WITHDRAW: required=${amount}, available=${portfolio.portfolio_balance}")
            raise InsufficientFundsException(float(amount), float(portfolio.portfolio_balance))

        logger.debug(f"WITHDRAW validated: new_balance will be ${new_balance}")

        return new_balance
    
    def get_transaction_by_id(self, transaction_id):
        return self.transactions_dao.get_transaction_by_id(transaction_id)
 
    def get_transactions_by_portfolio(self, portfolio_id):
        return self.transactions_dao.get_transactions_by_portfolio(portfolio_id)

    def get_transactions_by_asset(self, portfolio_id, asset_id):
        return self.transactions_dao.get_transaction_by_asset(asset_id)

    def get_transactions_by_type(self, transaction_type):
        return self.transactions_dao.get_transaction_by_type(transaction_type)

    def get_transactions_by_date_range(self, start_date, end_date):
        if start_date > end_date:
            raise InvalidDateRange(start_date, end_date)
        return self.transactions_dao.get_transactions_by_date_range(start_date, end_date)

    def get_transactions_by_portfolio_and_date_range(self, portfolio_id, start_date, end_date):
        if start_date > end_date:
                    raise InvalidDateRange(start_date, end_date)
        return self.transactions_dao.get_transactions_by_portfolio_and_date_range(portfolio_id, start_date, end_date)

    def get_transaction_count_by_portfolio(self, portfolio_id):
        return  self.transactions_dao.get_transaction_count_by_portfolio(portfolio_id)
    
    def get_total_transaction_value_by_portfolio(self, portfolio_id):
        return self.transactions_dao.get_total_transaction_value_by_portfolio(portfolio_id)

    def get_average_transaction_price_by_asset(self, asset_id):
        return self.transactions_dao.get_average_transaction_price_by_asset(asset_id)
    
    def get_transaction_summary_by_portfolio(self, portfolio_id):
        return self.transactions_dao.get_transaction_summary_by_portfolio(portfolio_id)
    
    def insert_transaction(self, portfolio_id, asset_id, transaction_type, transaction_quantity,
                            transaction_price, transaction_date, transaction_total, balance_after_transaction):
        logger.info(f"Updating transaction: portfolio_id={portfolio_id}, asset_id={asset_id}, transaction_type={transaction_type}, transaction_quantity={transaction_quantity}, transaction_price=${transaction_price}, transaction_total=${transaction_total}, balance_after_transaction={balance_after_transaction}")
                 
        self. _validate_portfolio_id(portfolio_id)
        self._validate_transaction_type(transaction_type)
    
        # validate asset_id, transaction_quantity, transaction_price for BUY and SELL 
        if transaction_type == "BUY" or "SELL":
            try:
                self.assets_dao.get_by_id(asset_id)
                logger.debug(f"Asset validated: {asset_id}")
            except Exception as e:
                raise AssetNotFoundException(asset_id) from e
            
            if not isinstance(transaction_quantity, int) or transaction_quantity <= 0:
                raise InvalidQuantityException(transaction_quantity)
    
            # Validate price
            if not isinstance(transaction_price, (int, float, Decimal)) or transaction_price <= 0:
                raise InvalidPriceException(transaction_price)   
                        
        # validate balance_after_instance is a non-negative number
        self.validate_monetary_input(self, balance_after_transaction)
        # validate transaction_total is a non-negative number
        self.validate_monetary_input(self, transaction_total)
                
        return self.transactions_dao.insert_transaction(portfolio_id, asset_id, transaction_type, transaction_quantity,
                            transaction_price, transaction_date, transaction_total, balance_after_transaction)

    def update_transaction(self, transaction_id, transaction_type, transaction_quantity,
                            transaction_price, transaction_total, balance_after_transaction):
        logger.info(f"Updating transaction: transaction_id={transaction_id}, transaction_type={transaction_type}, transaction_quantity={transaction_quantity}, transaction_price=${transaction_price}, transaction_total=${transaction_total}, balance_after_transaction={balance_after_transaction}")
                
        self. _validate_transaction_id(transaction_id)
        self._validate_transaction_type(transaction_type)
        
        # validate quantity
        if not isinstance(transaction_quantity, int) or transaction_quantity < 0:
            raise InvalidQuantityException(transaction_quantity)

        # Validate price
        if not isinstance(transaction_price, (int, float, Decimal)) or transaction_price < 0:
            raise InvalidPriceException(transaction_price)

        # validate balance_after_instance is a non-negative number
        self.validate_monetary_input(self, balance_after_transaction)
        # validate transaction_total is a non-negative number
        self.validate_monetary_input(self, transaction_total)

        
        return self.transactions_dao.update_transaction(transaction_id, transaction_type, transaction_quantity,
                            transaction_price, transaction_total, balance_after_transaction)

    def delete_transaction(self, transaction_id):
        logger.info(f"Deleting transaction: transaction_id={transaction_id}")
        self. _validate_transaction_id(transaction_id)
        return self.transactions_dao.delete_transaction(transaction_id)
  
    def delete_transactions_by_portfolio(self, portfolio_id):
        logger.info(f"Deleting transactions from portfolio: portfolio_id={portfolio_id}")
        self. _validate_portfolio_id(portfolio_id)
        return self.transactions_dao.delete_transactions_by_portfolio(portfolio_id)

    def get_portfolio_holdings(self, portfolio_id):
        logger.debug(f"Retrieving holdings for portfolio: {portfolio_id}")
        self._validate_portfolio_id(portfolio_id)
        return self.transactions_dao.get_portfolio_holdings(portfolio_id)

    def get_asset_holding(self, portfolio_id, asset_id):
        logger.debug(f"Retrieving holding for asset {asset_id} in portfolio: {portfolio_id}")
        self._validate_portfolio_id(portfolio_id)
        try:
            self.assets_dao.get_by_id(asset_id)
        except Exception as e:
            raise AssetNotFoundException(asset_id) from e
        quantity = self.transactions_dao.get_asset_holding(portfolio_id, asset_id)
        return {"asset_id": asset_id, "quantity": quantity}