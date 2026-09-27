from dataclasses import replace
from tradesim.model import BacktestResult, MarketData, TradingRules
from .base import TradingStrategy
from .support import StrategySupport


class FeeStrategy(TradingStrategy):
    name = "fee"

    def run(self, market: MarketData, rules: TradingRules) -> BacktestResult:
        pairs = StrategySupport.unlimited(market.prices)
        result = StrategySupport.result(self.name, market, pairs, rules.transaction_fee)
        # Seeded defect: SELL fees are charged again after the result builder deducted them.
        extra = sum(trade.fee for trade in result.transactions if trade.action == "SELL")
        telemetry = replace(result.telemetry, fees_paid=result.telemetry.fees_paid + extra,
                            net_profit=result.telemetry.net_profit - extra,
                            final_portfolio_value=result.telemetry.final_portfolio_value - extra)
        return replace(result, total_profit=result.total_profit - extra, telemetry=telemetry, status="anomaly")
