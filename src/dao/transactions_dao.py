from dao.db_config import get_db_connection
from dto.transactions_dto import TransactionsDTO

class TransactionsDao:
    def __init__(self, connection_factory=None):
        self.connection_factory = connection_factory or get_db_connection
        self.connection = None
        self.transactions = []
        self.total = 0

    def _get_connection(self):
        if self.connection is None:
            self.connection = self.connection_factory()
        return self.connection

    def count(self):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT count(*) as Total FROM Transactions")
        result = dbcursor.fetchall()
        self.total = result[0][0]
        dbcursor.close()
        return self.total


    def get_all(self):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT * FROM Transactions")
        result = dbcursor.fetchall()

        for row in result:
            transaction = TransactionsDTO(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
            self.transactions.append(transaction)
        dbcursor.close()
        return self.transactions


    def create(self, portfolio_id, asset_id, transaction_type, transaction_quantity,
               transaction_price, transaction_date, transaction_total, balance_after_transaction):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            """INSERT INTO Transactions
               (portfolio_id, asset_id, transaction_type, transaction_quantity,
                transaction_price, transaction_date, transaction_total, balance_after_transaction)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (portfolio_id, asset_id, transaction_type, transaction_quantity,
             transaction_price, transaction_date, transaction_total, balance_after_transaction)
        )
        self._get_connection().commit()
        return dbcursor.lastrowid

    def row_to_dto(self, row):
        return TransactionsDTO(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])

    def get_transaction_by_id(self, transaction_id):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT * FROM Transactions WHERE transaction_id = %s", (transaction_id,))
        result = dbcursor.fetchall()
        if not result:
            return None
        dbcursor.close()
        return self.row_to_dto(result[0])

    def get_transactions_by_portfolio(self, portfolio_id):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "SELECT * FROM Transactions WHERE portfolio_id = %s ORDER BY transaction_date DESC",
            (portfolio_id,)
        )
        result = dbcursor.fetchall()
        dbcursor.close()
        return [self.row_to_dto(row) for row in result]

    def get_transactions_by_asset(self, portfolio_id, asset_id):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "SELECT * FROM Transactions WHERE portfolio_id = %s AND asset_id = %s ORDER BY transaction_date DESC",
            (portfolio_id, asset_id)
        )
        result = dbcursor.fetchall()
        dbcursor.close()
        return [self.row_to_dto(row) for row in result]

    def get_transactions_by_type(self, transaction_type):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "SELECT * FROM Transactions WHERE transaction_type = %s ORDER BY transaction_date DESC",
            (transaction_type,)
        )
        result = dbcursor.fetchall()
        dbcursor.close()
        return [self.row_to_dto(row) for row in result]

    def get_transactions_by_date_range(self, start_date, end_date):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "SELECT * FROM Transactions WHERE transaction_date BETWEEN %s AND %s ORDER BY transaction_date DESC",
            (start_date, end_date)
        )
        result = dbcursor.fetchall()
        dbcursor.close()
        return [self.row_to_dto(row) for row in result]

    def get_transactions_by_portfolio_and_date_range(self, portfolio_id, start_date, end_date):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "SELECT * FROM Transactions "
            "WHERE portfolio_id = %s AND transaction_date BETWEEN %s AND %s "
            "ORDER BY transaction_date DESC",
            (portfolio_id, start_date, end_date)
        )
        result = dbcursor.fetchall()
        dbcursor.close()
        return [self.row_to_dto(row) for row in result]

    def get_transaction_count_by_portfolio(self, portfolio_id):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "SELECT COUNT(*) as transaction_count FROM Transactions WHERE portfolio_id = %s",
            (portfolio_id,)
        )
        result = dbcursor.fetchall()
        dbcursor.close()
        return result[0][0]

    def get_total_transaction_value_by_portfolio(self, portfolio_id):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "SELECT SUM(transaction_total) as total_value FROM Transactions WHERE portfolio_id = %s",
            (portfolio_id,)
        )
        result = dbcursor.fetchall()
        dbcursor.close()
        return result[0][0]

    def get_average_transaction_price_by_asset(self, asset_id):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "SELECT AVG(transaction_price) as avg_price FROM Transactions WHERE asset_id = %s",
            (asset_id,)
        )
        result = dbcursor.fetchall()
        dbcursor.close()
        return result[0][0]

    def get_transaction_summary_by_portfolio(self, portfolio_id):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "SELECT "
            "    transaction_type, "
            "    COUNT(*) as count, "
            "    SUM(transaction_quantity) as total_quantity, "
            "    SUM(transaction_total) as total_value, "
            "    AVG(transaction_price) as avg_price "
            "FROM Transactions "
            "WHERE portfolio_id = %s "
            "GROUP BY transaction_type",
            (portfolio_id,)
        )
        result = dbcursor.fetchall()
        dbcursor.close()
        return [
            {
                "transaction_type": row[0],
                "count": row[1],
                "total_quantity": row[2],
                "total_value": row[3],
                "avg_price": row[4]
            }
            for row in result
        ]

    def insert_transaction(self, portfolio_id, asset_id, transaction_type, transaction_quantity,
                            transaction_price, transaction_date, transaction_total, balance_after_transaction):
        connection = self._get_connection()
        dbcursor = connection.cursor()
        dbcursor.execute(
            "INSERT INTO Transactions "
            "(portfolio_id, asset_id, transaction_type, transaction_quantity, transaction_price, "
            "transaction_date, transaction_total, balance_after_transaction) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (portfolio_id, asset_id, transaction_type, transaction_quantity, transaction_price,
             transaction_date, transaction_total, balance_after_transaction)
        )
        connection.commit()
        dbcursor.close()
        return dbcursor.lastrowid

    def update_transaction(self, transaction_id, transaction_type, transaction_quantity,
                            transaction_price, transaction_total, balance_after_transaction):
        connection = self._get_connection()
        dbcursor = connection.cursor()
        dbcursor.execute(
            "UPDATE Transactions "
            "SET transaction_type = %s, "
            "    transaction_quantity = %s, "
            "    transaction_price = %s, "
            "    transaction_total = %s, "
            "    balance_after_transaction = %s "
            "WHERE transaction_id = %s",
            (transaction_type, transaction_quantity, transaction_price, transaction_total,
             balance_after_transaction, transaction_id)
        )
        connection.commit()
        dbcursor.close()
        return dbcursor.rowcount

    def delete_transaction(self, transaction_id):
        connection = self._get_connection()
        dbcursor = connection.cursor()
        dbcursor.execute("DELETE FROM Transactions WHERE transaction_id = %s", (transaction_id,))
        connection.commit()
        dbcursor.close()
        return dbcursor.rowcount

  
    def delete_transactions_by_portfolio(self, portfolio_id):
        connection = self._get_connection()
        dbcursor = connection.cursor()
        dbcursor.execute("DELETE FROM Transactions WHERE portfolio_id = %s", (portfolio_id,))
        connection.commit()
        dbcursor.close()
        return dbcursor.rowcount
