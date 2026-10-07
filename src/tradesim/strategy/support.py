from dataclasses import replace
from tradesim.model import BacktestResult, MarketData, Telemetry, Trade


class StrategySupport:
    @staticmethod
    def result(name: str, market: MarketData, pairs: list[tuple[int, int]], fee: float,
               cooldown_days: int = 0) -> BacktestResult:
        prices = market.prices
        trades: list[Trade] = []
        gross = fees = 0.0
        observed = 0
        last_sell = None
        for buy, sell in sorted(pairs):
            if buy < 0 or sell >= len(prices) or buy >= sell:
                continue
            if last_sell is not None:
                observed = max(observed, buy - last_sell - 1)
            gross += prices[sell] - prices[buy]
            fees += 2 * fee
            trades.extend((Trade("BUY", buy, prices[buy], fee, 0.0),
                           Trade("SELL", sell, prices[sell], fee, prices[sell] - prices[buy])))
            last_sell = sell
        net = gross - fees
        equity = peak = 0.0
        max_drawdown = 0.0
        for trade in trades:
            equity += trade.realized_profit - trade.fee
            peak = max(peak, equity)
            if peak > 0:
                max_drawdown = max(max_drawdown, (peak - equity) / peak)
        telemetry = Telemetry(days_processed=len(prices), buy_signals=len(pairs), sell_signals=len(pairs),
                              fees_paid=fees, cooldown_days_observed=observed,
                              peak_portfolio_value=peak, final_portfolio_value=net,
                              gross_profit=gross, net_profit=net)
        return BacktestResult(name, net, len(trades) // 2, max_drawdown, "valid", trades, telemetry)

    @staticmethod
    def anomaly(result: BacktestResult) -> BacktestResult:
        return replace(result, status="anomaly")

    @staticmethod
    def unlimited(prices: list[float]) -> list[tuple[int, int]]:
        pairs: list[tuple[int, int]] = []
        i, n = 0, len(prices)
        while i < n - 1:
            while i < n - 1 and prices[i + 1] <= prices[i]:
                i += 1
            buy = i
            while i < n - 1 and prices[i + 1] >= prices[i]:
                i += 1
            if i > buy:
                pairs.append((buy, i))
        return pairs
