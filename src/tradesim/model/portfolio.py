from dataclasses import dataclass, field
from .trade import Trade


@dataclass
class Portfolio:
    trades: list[Trade] = field(default_factory=list)
    cash: float = 0.0
    entry_price: float | None = None
    open_positions: int = 0
    fees_paid: float = 0.0

    def buy(self, day: int, price: float, fee: float = 0.0) -> Trade:
        if self.open_positions:
            raise ValueError("A position is already open")
        trade = Trade("BUY", day, price, fee, 0.0)
        self.trades.append(trade)
        self.entry_price, self.open_positions = price, 1
        self.cash -= price + fee
        self.fees_paid += fee
        return trade

    def sell(self, day: int, price: float, fee: float = 0.0) -> Trade:
        if not self.open_positions or self.entry_price is None:
            raise ValueError("No open position to sell")
        profit = price - self.entry_price
        trade = Trade("SELL", day, price, fee, profit)
        self.trades.append(trade)
        self.cash += price - fee
        self.fees_paid += fee
        self.open_positions, self.entry_price = 0, None
        return trade
