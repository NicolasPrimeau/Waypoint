from enum import Enum
from typing import Optional


class StockExchangeCode(str, Enum):
    Toronto = "to"

    def __str__(self):
        return self.value


class Ticker:
    def __init__(self, ticker: str, exchange: Optional[StockExchangeCode] = None):
        if "." in ticker:
            parts = ticker.split(".")
            self.ticker = parts[0].upper()
            self.exchange = StockExchangeCode(parts[1].lower())
        else:
            self.ticker = ticker.upper()
            self.exchange = exchange

    def __str__(self):
        return f"{self.ticker}.{str(self.exchange)}" if self.exchange else self.ticker

    def __repr__(self):
        return str(self)
