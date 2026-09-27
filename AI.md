# TradeSim Python — system context

TradeSim is an in-memory daily-price backtesting service. It has no runtime dependencies outside Python 3.10+.

## Execution pipeline

`MarketDataRepository` builds deterministic `PricePoint` sequences. `PolicyEngine` selects a strategy, each strategy returns buy/sell day pairs, and `StrategySupport.result` turns those pairs into immutable `Trade` records and a `BacktestResult` with fees, profit, drawdown, and telemetry. The HTTP handler maps JSON requests to engine calls and serializes dataclasses for the dashboard.

## Data relationships

- A `MarketData` owns ordered daily points and exposes their closing prices.
- A pair `(buy_day, sell_day)` uses zero-based indices into that market data.
- A `Portfolio` records fills, cash, open shares, entry price, and paid fees.
- `TradingRules` apply transaction limits, per-fill fees, and the mandatory gap between a sale and a subsequent purchase.
- A `BacktestResult` contains the strategy name, trades, profit, drawdown, validity status, and `Telemetry`.

## Debugging invariants

1. Trade days are monotonically non-decreasing; each BUY is strictly before its SELL.
2. A completed position uses one BUY and one SELL; `transaction_count` is the number of completed pairs.
3. Net profit equals gross profit minus all fees exactly once.
4. Result building does not mutate its inputs or previously returned results.
5. Each backtest is isolated; one run must not affect another run's profit or telemetry.
6. A cooldown of `d` days requires the next BUY day to be strictly greater than `last_sell_day + d`.
7. The dashboard incident banner is healthy only when every returned result has status `valid`.

The initial challenge intentionally violates invariants in SingleTradeStrategy, UnlimitedStrategy, LimitedTransactionStrategy, FeeStrategy, CooldownStrategy, and PolicyEngine. The defects are documented in README.md and surfaced by `tests/test_runner.py`.
