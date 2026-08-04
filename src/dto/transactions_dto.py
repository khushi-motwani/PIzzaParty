class TransactionsDTO:
    def __init__(self, transaction_id=None, portfolio_id=None, asset_id=None, transaction_type="UNKNOWN", transaction_quantity=0, transaction_price=None, transaction_date=None, transaction_total=0, balance_after_transaction=0):
        self.transaction_id = transaction_id
        self.portfolio_id = portfolio_id
        self.asset_id = asset_id
        self.transaction_type = transaction_type
        self.transaction_quantity = transaction_quantity
        self.transaction_price = transaction_price
        self.transaction_date = transaction_date
        self.transaction_total = transaction_total
        self.balance_after_transaction = balance_after_transaction

    def __str__(self):
        return f"TransactionsDTO(transaction_id={self.transaction_id}, portfolio_id={self.portfolio_id}, asset_id={self.asset_id}, transaction_type={self.transaction_type}, transaction_quantity={self.transaction_quantity}, transaction_price={self.transaction_price}, transaction_date={self.transaction_date}, transaction_total={self.transaction_total}, balance_after_transaction={self.balance_after_transaction})"

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "portfolio_id": self.portfolio_id,
            "asset_id": self.asset_id,
            "transaction_type": self.transaction_type,
            "transaction_quantity": self.transaction_quantity,
            "transaction_price": self.transaction_price,
            "transaction_date": self.transaction_date,
            "transaction_total": self.transaction_total,
            "balance_after_transaction": self.balance_after_transaction
        }
