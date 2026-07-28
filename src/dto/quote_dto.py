class QuoteDTO:
    def __init__(self, ticker, price, currency="USD", previous_close=None, market_cap=None, day_high=None, day_low=None):
        self.ticker = ticker
        self.price = price
        self.currency = currency
        self.previous_close = previous_close
        self.market_cap = market_cap
        self.day_high = day_high
        self.day_low = day_low

    def __str__(self):
        return f"QuoteDTO(ticker={self.ticker}, price={self.price}, currency={self.currency}, previous_close={self.previous_close}, market_cap={self.market_cap}, day_high={self.day_high}, day_low={self.day_low})"

    def to_dict(self):
        return {
            "ticker": self.ticker,
            "price": self.price,
            "currency": self.currency,
            "previous_close": self.previous_close,
            "market_cap": self.market_cap,
            "day_high": self.day_high,
            "day_low": self.day_low
        }
