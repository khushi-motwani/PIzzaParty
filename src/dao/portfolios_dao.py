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

    def count(self):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT count(*) as Total FROM Portfolios")
        result = dbcursor.fetchall()
        self.total = result[0][0]
        return self.total


    def get_all(self):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT * FROM Portfolios")
        result = dbcursor.fetchall()

        for row in result:
            portfolio = PortfoliosDTO(row[1], row[2], row[0])
            self.portfolios.append(portfolio)
        return self.portfolios


    def get_by_id(self, portfolio_id):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("SELECT * FROM Portfolios WHERE portfolio_id = %s", (portfolio_id,))
        result = dbcursor.fetchone()

        if result is None:
            raise PortfolioNotFoundException(portfolio_id)

        return PortfoliosDTO(result[1], result[2], result[0])


    def update_balance(self, portfolio_id, new_balance):
        dbcursor = self._get_connection().cursor()
        dbcursor.execute("UPDATE Portfolios SET portfolio_balance = %s WHERE portfolio_id = %s",
                        (new_balance, portfolio_id))
        self._get_connection().commit()
        return dbcursor.rowcount > 0
        self.connection.commit()
        return dbcursor.rowcount > 0
