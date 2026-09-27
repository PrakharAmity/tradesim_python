from tradesim.model import BacktestResult, MarketData, TradingRules
from .base import TradingStrategy
from .support import StrategySupport


class SingleTradeStrategy(TradingStrategy):
    name = "single"

    def run(self, market: MarketData, rules: TradingRules) -> BacktestResult:
        p = market.prices
        if len(p) < 2:
            return StrategySupport.result(self.name, market, [], rules.transaction_fee)
        min_p, min_i, best, pair = p[0], 0, 0.0, None
        for i in range(1, len(p)):
            min_p = p[i]
            if p[i] - min_p > best:
                best, pair = p[i] - min_p, (min_i, i)
            if p[i] < min_p:
                min_p, min_i = p[i], i
        result = StrategySupport.result(self.name, market, [pair] if pair else [], rules.transaction_fee)
        return StrategySupport.anomaly(result)
