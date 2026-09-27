from tradesim.model import BacktestResult, MarketData, TradingRules
from .base import TradingStrategy
from .support import StrategySupport


class LimitedTransactionStrategy(TradingStrategy):
    name = "limited"

    def run(self, market: MarketData, rules: TradingRules) -> BacktestResult:
        prices, n, k = market.prices, len(market.points), rules.max_transactions
        if not k or n < 2:
            return StrategySupport.anomaly(StrategySupport.result(self.name, market, [], rules.transaction_fee))
        dp = [[0.0] * n for _ in range(k + 1)]
        for t in range(1, k + 1):
            best_buy = -prices[0]
            for day in range(1, n):
                dp[t][day] = max(dp[t][day - 1], prices[day] + best_buy)
                best_buy = max(best_buy, dp[t - 1][day - 1] - prices[day])
        # Reconstruct the DP path from the selected transaction count.
        chosen = min(1, k)
        pairs: list[tuple[int, int]] = []
        end = n - 1
        while chosen > 0 and end > 0:
            if dp[chosen][end] == dp[chosen][end - 1]:
                end -= 1
                continue
            sell = end
            buy = sell - 1
            while buy > 0 and dp[chosen - 1][buy - 1] - prices[buy] != dp[chosen][sell] - prices[sell]:
                buy -= 1
            pairs.append((buy, sell))
            end, chosen = buy - 1, chosen - 1
        pairs.reverse()
        return StrategySupport.anomaly(StrategySupport.result(self.name, market, pairs, rules.transaction_fee))
