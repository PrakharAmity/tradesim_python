from dataclasses import dataclass


@dataclass(frozen=True)
class TradingRules:
    max_transactions: int = 2
    transaction_fee: float = 2.0
    cooldown_days: int = 1

    def __post_init__(self) -> None:
        if self.max_transactions < 0 or self.transaction_fee < 0 or self.cooldown_days < 0:
            raise ValueError("Trading rule values cannot be negative")
