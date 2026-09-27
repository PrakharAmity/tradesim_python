from dataclasses import dataclass, field
from .trade import Trade


@dataclass(frozen=True)
class Telemetry:
    days_processed: int = 0
    buy_signals: int = 0
    sell_signals: int = 0
    fees_paid: float = 0.0
    cooldown_days_observed: int = 0
    peak_portfolio_value: float = 0.0
    final_portfolio_value: float = 0.0
    gross_profit: float = 0.0
    net_profit: float = 0.0


@dataclass(frozen=True)
class BacktestResult:
    strategy: str
    total_profit: float
    transaction_count: int
    max_drawdown: float
    status: str
    transactions: list[Trade] = field(default_factory=list)
    telemetry: Telemetry = field(default_factory=Telemetry)
