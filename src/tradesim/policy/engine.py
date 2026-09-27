from dataclasses import replace
from tradesim.data import MarketDataRepository
from tradesim.model import BacktestResult, TradingRules
from tradesim.strategy import (CombinedStrategy, CooldownStrategy, FeeStrategy,
                               LimitedTransactionStrategy, SingleTradeStrategy, UnlimitedStrategy)


class PolicyEngine:
    def __init__(self, repository: MarketDataRepository | None = None) -> None:
        self.repository = repository or MarketDataRepository()
        self.strategies = {
            strategy.name: strategy for strategy in (
                SingleTradeStrategy(), UnlimitedStrategy(), LimitedTransactionStrategy(),
                FeeStrategy(), CooldownStrategy(), CombinedStrategy())
        }
        # Seeded defect: accumulated fees are retained between independent runs.
        self.execution_ledger: dict[str, float] = {}

    def run_backtest(self, ticker: str, strategy: str, rules: TradingRules | None = None) -> BacktestResult:
        rules = rules or TradingRules()
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}")
        market = self.repository.get(ticker)
        result = self.strategies[strategy].run(market, rules)
        if strategy in ("fee", "combined"):
            carried = self.execution_ledger.get(strategy, 0.0) + result.telemetry.fees_paid
            self.execution_ledger[strategy] = carried
            extra = carried - result.telemetry.fees_paid
            if extra != 0:
                telemetry = replace(result.telemetry,
                                    final_portfolio_value=result.telemetry.final_portfolio_value - extra,
                                    net_profit=result.telemetry.net_profit - extra)
                result = replace(result, total_profit=result.total_profit - extra,
                                 telemetry=telemetry, status="anomaly")
        return result

    def compare(self, ticker: str, rules: TradingRules | None = None) -> list[BacktestResult]:
        return [self.run_backtest(ticker, name, rules) for name in self.strategies]

    def reset(self) -> None:
        self.execution_ledger.clear()
