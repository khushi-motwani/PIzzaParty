from dao.db_config import get_db_connection
from dto.transactions_dto import TransactionsDTO

class TransactionsDao:
    def __init__(self):
        self.connection = get_db_connection()
        self.transactions = []
        self.total = 0


    def count(self):
        dbcursor = self.connection.cursor()
        dbcursor.execute("SELECT count(*) as Total FROM Transactions")
        result = dbcursor.fetchall()
        self.total = result[0][0]
        return self.total


    def get_all(self):
        dbcursor = self.connection.cursor()
        dbcursor.execute("SELECT * FROM Transactions")
        result = dbcursor.fetchall()

        for row in result:
            transaction = TransactionsDTO(row[1], row[3], row[4], row[6], row[7], row[8], row[0], row[2], row[5])
            self.transactions.append(transaction)
        return self.transactions


    def create(self, portfolio_id, asset_id, transaction_type, transaction_quantity,
               transaction_price, transaction_date, transaction_total, balance_after_transaction):
        dbcursor = self.connection.cursor()
        dbcursor.execute(
            """INSERT INTO Transactions
               (portfolio_id, asset_id, transaction_type, transaction_quantity,
                transaction_price, transaction_date, transaction_total, balance_after_transaction)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (portfolio_id, asset_id, transaction_type, transaction_quantity,
             transaction_price, transaction_date, transaction_total, balance_after_transaction)
        )
        self.connection.commit()
        return dbcursor.lastrowid
