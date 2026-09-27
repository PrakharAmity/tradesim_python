from abc import ABC, abstractmethod
from tradesim.model import BacktestResult, MarketData, TradingRules


class TradingStrategy(ABC):
    name = "base"

    @abstractmethod
    def run(self, market: MarketData, rules: TradingRules) -> BacktestResult:
        raise NotImplementedError
