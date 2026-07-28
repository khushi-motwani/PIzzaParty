from dao.portfolios_dao import PortfoliosDao

class PortfoliosService:
    def __init__(self):
        self.portfolios_dao = PortfoliosDao()

    # ==================== GETTER OPERATIONS ====================

    def get_all(self):
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
        return self.portfolios_dao.count()

    def get_sorted_by_balance_desc(self):
        return self.portfolios_dao.get_sorted_by_balance_desc()

    def get_sorted_by_balance_asc(self):
        return self.portfolios_dao.get_sorted_by_balance_asc()

    # ==================== SETTER OPERATIONS ====================

    def create(self, portfolio_name, portfolio_balance=0):
        return self.portfolios_dao.create(portfolio_name, portfolio_balance)

    def update_name(self, portfolio_id, portfolio_name):
        return self.portfolios_dao.update_name(portfolio_id, portfolio_name)

    def update_balance(self, portfolio_id, new_balance):
        return self.portfolios_dao.update_balance(portfolio_id, new_balance)

    def increment_balance(self, portfolio_id, amount):
        return self.portfolios_dao.increment_balance(portfolio_id, amount)

    def decrement_balance(self, portfolio_id, amount):
        return self.portfolios_dao.decrement_balance(portfolio_id, amount)

    def delete(self, portfolio_id):
        return self.portfolios_dao.delete(portfolio_id)
