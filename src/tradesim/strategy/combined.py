from tradesim.model import BacktestResult, MarketData, TradingRules
from .base import TradingStrategy
from .support import StrategySupport


class CombinedStrategy(TradingStrategy):
    name = "combined"

    def run(self, market: MarketData, rules: TradingRules) -> BacktestResult:
        prices = market.prices
        n, k, fee, cool = len(prices), rules.max_transactions, rules.transaction_fee, rules.cooldown_days
        # State key is (position_open, completed_sales, last_sell_day). Each value
        # stores realized net profit, completed pairs, and an optional buy index.
        states: dict[tuple[bool, int, int], tuple[float, list[tuple[int, int]], int | None]] = {
            (False, 0, -10**9): (0.0, [], None)
        }
        for day, price in enumerate(prices):
            next_states = dict(states)  # wait one day without changing position
            for (is_open, sales, last_sell), (profit, pairs, buy_day) in states.items():
                if is_open:
                    if sales < k:
                        key = (False, sales + 1, day)
                        candidate = (profit + price - fee, pairs + [(buy_day, day)], None)
                        if key not in next_states or candidate[0] > next_states[key][0]:
                            next_states[key] = candidate
                elif sales < k and day > last_sell + cool:
                    key = (True, sales, last_sell)
                    candidate = (profit - price, pairs, day)
                    if key not in next_states or candidate[0] > next_states[key][0]:
                        next_states[key] = candidate
            states = next_states
        options = [value for (is_open, _, _), value in states.items() if not is_open]
        pairs = max(options, key=lambda value: value[0], default=(0.0, [], None))[1]
        return StrategySupport.result(self.name, market, pairs, fee, cool)
