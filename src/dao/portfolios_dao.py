from dao.db_config import get_db_connection
from dto.portfolios_dto import PortfoliosDTO
from exception.validation_exceptions import PortfolioNotFoundException

class PortfoliosDao:
    def __init__(self):
        self.connection = get_db_connection()
        self.portfolios = []
        self.total = 0


    def count(self):
        dbcursor = self.connection.cursor()
        dbcursor.execute("SELECT count(*) as Total FROM Portfolios")
        result = dbcursor.fetchall()
        self.total = result[0][0]
        return self.total


    def get_all(self):
        dbcursor = self.connection.cursor()
        dbcursor.execute("SELECT * FROM Portfolios")
        result = dbcursor.fetchall()

        for row in result:
            portfolio = PortfoliosDTO(row[1], row[2], row[0])
            self.portfolios.append(portfolio)
        return self.portfolios


    def get_by_id(self, portfolio_id):
        dbcursor = self.connection.cursor()
        dbcursor.execute("SELECT * FROM Portfolios WHERE portfolio_id = %s", (portfolio_id,))
        result = dbcursor.fetchone()

        if result is None:
            raise PortfolioNotFoundException(portfolio_id)

        return PortfoliosDTO(result[1], result[2], result[0])


    def update_balance(self, portfolio_id, new_balance):
        dbcursor = self.connection.cursor()
        dbcursor.execute("UPDATE Portfolios SET portfolio_balance = %s WHERE portfolio_id = %s",
                        (new_balance, portfolio_id))
        self.connection.commit()
        return dbcursor.rowcount > 0
