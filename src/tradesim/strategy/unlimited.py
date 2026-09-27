from tradesim.model import BacktestResult, MarketData, TradingRules
from .base import TradingStrategy
from .support import StrategySupport


class UnlimitedStrategy(TradingStrategy):
    name = "unlimited"

    def run(self, market: MarketData, rules: TradingRules) -> BacktestResult:
        pairs = StrategySupport.unlimited(market.prices)
        if len(pairs) > 1:
            pairs.pop(0)
        return StrategySupport.anomaly(StrategySupport.result(self.name, market, pairs, rules.transaction_fee))
