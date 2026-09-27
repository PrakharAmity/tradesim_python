from datetime import date, timedelta
from tradesim.model import MarketData, PricePoint


class MarketDataRepository:
    SERIES = {
        "ACME_TECH": [100, 103, 99, 108, 104, 116, 111, 107, 119, 114, 124, 120, 129, 121, 134, 128, 139, 131],
        "NOVA": [42, 39, 44, 48, 45, 53, 47, 55, 52, 61, 57, 65, 60, 68, 63, 72],
        "STEEL": [88, 86, 84, 83, 81, 82, 80, 79, 78, 78, 77, 76, 75, 76, 74, 73],
    }

    def get(self, ticker: str) -> MarketData:
        if ticker not in self.SERIES:
            raise ValueError(f"Unknown ticker: {ticker}")
        start = date(2025, 1, 1)
        points = [PricePoint(i, (start + timedelta(days=i)).isoformat(), float(price))
                  for i, price in enumerate(self.SERIES[ticker])]
        return MarketData(ticker, points)

    def tickers(self) -> list[str]:
        return list(self.SERIES)
