from dataclasses import dataclass


@dataclass(frozen=True)
class Trade:
    action: str
    day: int
    price: float
    fee: float
    realized_profit: float = 0.0
