class PortfoliosDTO:
    def __init__(self, portfolio_name, portfolio_id=None, portfolio_balance=0):
        self.portfolio_id = portfolio_id
        self.portfolio_name = portfolio_name
        self.portfolio_balance = portfolio_balance

    def __str__(self):
        return f"PortfoliosDTO(portfolio_id={self.portfolio_id}, portfolio_name={self.portfolio_name}, portfolio_balance={self.portfolio_balance})"

    def to_dict(self):
        return {
            "portfolio_id": self.portfolio_id,
            "portfolio_name": self.portfolio_name,
            "portfolio_balance": self.portfolio_balance
        }
