from client.finance_client import FinanceClient


class FinanceService:
    def __init__(self, client=None):
        self.finance_client = client or FinanceClient()

    def get_quote(self, ticker):
        return self.finance_client.get_quote(ticker)
