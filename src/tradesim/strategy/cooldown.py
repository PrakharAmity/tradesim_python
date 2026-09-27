from tradesim.model import BacktestResult, MarketData, TradingRules
from .base import TradingStrategy
from .support import StrategySupport


class CooldownStrategy(TradingStrategy):
    name = "cooldown"

    def run(self, market: MarketData, rules: TradingRules) -> BacktestResult:
        prices = market.prices
        candidates = StrategySupport.unlimited(prices)
        pairs: list[tuple[int, int]] = []
        last_sell = -10**9
        for buy, sell in candidates:
            if buy < last_sell + rules.cooldown_days:
                continue
            pairs.append((buy, sell))
            last_sell = sell
        return StrategySupport.anomaly(StrategySupport.result(self.name, market, pairs, rules.transaction_fee,
                                                              rules.cooldown_days))
