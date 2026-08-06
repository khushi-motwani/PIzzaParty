from dao.db_config import get_db_connection
from dto.portfolios_dto import PortfoliosDTO
from exception.validation_exceptions import PortfolioNotFoundException

class PortfoliosDao:
    def __init__(self, connection_factory=None):
        self.connection_factory = connection_factory or get_db_connection
        self.connection = None
        self.portfolios = []
        self.total = 0

    def _get_connection(self):
        if self.connection is None:
            self.connection = self.connection_factory()
        return self.connection

    def _reset_connection(self):
        self.connection = None

    def get_all(self):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT * FROM Portfolios ORDER BY portfolio_id")
        result = dbcursor.fetchall()
        dbcursor.close()

        self.portfolios = []
        for row in result:
            portfolio = PortfoliosDTO(
                portfolio_name=row[1],
                portfolio_id=row[0],
                portfolio_balance=row[2]
            )
            self.portfolios.append(portfolio)
        return self.portfolios

    def get_by_id(self, portfolio_id):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT * FROM Portfolios WHERE portfolio_id = %s", (portfolio_id,))
        result = dbcursor.fetchone()
        dbcursor.close()

        if result is None:
            raise PortfolioNotFoundException(portfolio_id)

        return PortfoliosDTO(
            portfolio_name=result[1],
            portfolio_id=result[0],
            portfolio_balance=result[2]
        )

    def get_portfolio_balance(self, portfolio_id):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "SELECT portfolio_id, portfolio_name, portfolio_balance FROM Portfolios WHERE portfolio_id = %s",
            (portfolio_id,)
        )
        result = dbcursor.fetchone()
        dbcursor.close()

        if result is None:
            raise PortfolioNotFoundException(portfolio_id)

        return PortfoliosDTO(
            portfolio_name=result[1],
            portfolio_id=result[0],
            portfolio_balance=result[2]
        )

    def get_total_balance(self):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT SUM(portfolio_balance) as total_balance FROM Portfolios")
        result = dbcursor.fetchone()
        dbcursor.close()

        return result[0] if result[0] is not None else 0

    def get_count(self):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT COUNT(*) as total_portfolios FROM Portfolios")
        result = dbcursor.fetchone()
        dbcursor.close()
        self.total = result[0]
        return self.total

    def count(self):
        return self.get_count()

    def get_sorted_by_balance_desc(self):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT * FROM Portfolios ORDER BY portfolio_balance DESC")
        result = dbcursor.fetchall()
        dbcursor.close()

        self.portfolios = []
        for row in result:
            portfolio = PortfoliosDTO(
                portfolio_name=row[1],
                portfolio_id=row[0],
                portfolio_balance=row[2]
            )
            self.portfolios.append(portfolio)
        return self.portfolios

    def get_sorted_by_balance_asc(self):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT * FROM Portfolios ORDER BY portfolio_balance ASC")
        result = dbcursor.fetchall()
        dbcursor.close()

        self.portfolios = []
        for row in result:
            portfolio = PortfoliosDTO(
                portfolio_name=row[1],
                portfolio_id=row[0],
                portfolio_balance=row[2]
            )
            self.portfolios.append(portfolio)
        return self.portfolios

    def create(self, portfolio_name, portfolio_balance=0):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "INSERT INTO Portfolios (portfolio_name, portfolio_balance) VALUES (%s, %s)",
            (portfolio_name, portfolio_balance)
        )
        self._get_connection().commit()
        return dbcursor.lastrowid

    def update_name(self, portfolio_id, portfolio_name):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "UPDATE Portfolios SET portfolio_name = %s WHERE portfolio_id = %s",
            (portfolio_name, portfolio_id)
        )
        self._get_connection().commit()
        return dbcursor.rowcount > 0

    def update_balance(self, portfolio_id, new_balance):
        connection = self._get_connection()
        dbcursor = connection.cursor()
        dbcursor.execute(
            "UPDATE Portfolios SET portfolio_balance = %s WHERE portfolio_id = %s",
            (new_balance, portfolio_id)
        )
        connection.commit()
        dbcursor.close()
        self._reset_connection()
        return dbcursor.rowcount > 0

    def increment_balance(self, portfolio_id, amount):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "UPDATE Portfolios SET portfolio_balance = portfolio_balance + %s WHERE portfolio_id = %s",
            (amount, portfolio_id)
        )
        self._get_connection().commit()
        return dbcursor.rowcount > 0

    def decrement_balance(self, portfolio_id, amount):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "UPDATE Portfolios SET portfolio_balance = portfolio_balance - %s WHERE portfolio_id = %s",
            (amount, portfolio_id)
        )
        self._get_connection().commit()
        return dbcursor.rowcount > 0

    def delete(self, portfolio_id):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute(
            "DELETE FROM Portfolios WHERE portfolio_id = %s",
            (portfolio_id,)
        )
        self._get_connection().commit()
        return dbcursor.rowcount > 0
