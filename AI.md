# TradeSim Python

## Description

TradeSim Python is a Python 3.10+ market backtesting engine and execution-policy analytics dashboard. It simulates algorithmic trading strategies on historical price series, models multi-dimensional execution constraints (transaction fees, transaction limits, and mandatory cooldown periods), inspects granular fill ledgers, and visualizes performance telemetry in an isolated in-memory environment. It runs as a lightweight HTTP service with a browser dashboard, standard-library-only REST endpoints, and an in-memory market data catalog.

## Repository Structure

```text
tradesim_python/
├── challenge.json          Isolated runtime, port, install, start, and test configuration
├── pyproject.toml          Package metadata and project entry point definitions
├── start.bat               Server start launcher script (Windows CMD)
├── start.ps1               Server start launcher script (PowerShell)
├── start.sh                Server start entrypoint script (Unix)
├── src/
│   └── tradesim/
│       ├── __init__.py     Package initialization and export definitions
│       ├── main.py         Application entrypoint launching HTTP server
│       ├── data/
│       │   ├── __init__.py Package exports
│       │   └── repository.py In-memory market dataset repository (ACME_TECH, NOVA, STEEL)
│       ├── http/
│       │   ├── __init__.py Package exports
│       │   └── server.py   HTTP server, REST routing (/api/state, /api/backtest, /api/reset), and asset handler
│       ├── model/
│       │   ├── __init__.py Domain model exports
│       │   ├── backtest_result.py Backtest execution result data class and status
│       │   ├── market_data.py Price series container
│       │   ├── portfolio.py Portfolio telemetry, ledger, and accounting dataclasses
│       │   ├── price_point.py Daily market price record
│       │   ├── trade.py    Execution fill record (BUY/SELL)
│       │   └── trading_rules.py Execution constraints (max_transactions, fee, cooldown)
│       ├── policy/
│       │   ├── __init__.py Package exports
│       │   └── engine.py   Policy orchestration engine and backtest runner
│       ├── resources/
│       │   └── web/
│       │       ├── app.js      Dashboard query handling, API communication, SVG chart & ledger rendering
│       │       ├── index.html  Dashboard page markup and metric containers
│       │       └── style.css   Dark glassmorphic responsive styling
│       └── strategy/
│           ├── __init__.py Strategy catalog exports
│           ├── base.py     Trading strategy abstract base class
│           ├── combined.py Multi-constraint composite trading strategy
│           ├── cooldown.py Mandatory rest interval trading strategy
│           ├── fee.py      Per-fill transaction fee trading strategy
│           ├── limited.py  Bounded dynamic programming (k transactions) strategy
│           ├── single_trade.py Single optimal round-trip trade strategy
│           ├── support.py  Dynamic programming solver, swing detector, and result builder
│           └── unlimited.py Unlimited valley-to-peak swing trading strategy
├── test/
│   ├── __init__.py         Test package marker
│   ├── test_cooldown.py    Cooldown period enforcement unit tests
│   ├── test_fee.py         Fee deduction accounting unit tests
│   ├── test_limited.py     k-transaction dynamic programming unit tests
│   ├── test_policy_engine.py PolicyEngine backtest isolation unit tests
│   ├── test_single_trade.py Single-trade optimal profit unit tests
│   └── test_unlimited.py   Unlimited swing trade profit unit tests
├── tests/
│   ├── run_tests.bat       Automated test suite batch script (Windows CMD)
│   ├── run_tests.ps1       Automated test suite PowerShell runner
│   ├── run_tests.sh        Incremental test rebuild and JSON test runner entrypoint (Unix)
│   └── test_runner.py      Six behavioral challenge tests and JSON protocol runner
└── README.md               Candidate-facing application and bug reproduction guide
```

## Bugs and Bug Locations

These are the six behavioral bug surfaces covered by the challenge. The named locations identify the owning implementation areas for debugging and review.

### 1. Single trade strategy returns zero profit

- **Bug location:** `src/tradesim/strategy/single_trade.py`, `SingleTradeStrategy.run`
- **How to observe it:** In the dashboard, select the `Single` strategy for ticker `ACME_TECH` (or benchmark price series `[3, 1, 8]`) and click **Run Backtest**, or execute `python tests/test_runner.py` / `python -m unittest test/test_single_trade.py`.
- **Failure:** Gross profit is reported as $0.00 and status is marked as `anomaly` because `min_p = p[i]` resets the running minimum price on every iteration inside the loop before evaluating profit potential (`p[i] - min_p > best`).
- **Expected:** The strategy preserves historical minimum prices across earlier days, captures the global optimal single round-trip buy/sell trade (yielding $7.00 gross profit on benchmark series `[3, 1, 8]`), and returns status `valid`.

### 2. Unlimited swing trading strategy discards the first profitable cycle

- **Bug location:** `src/tradesim/strategy/unlimited.py`, `UnlimitedStrategy.run`
- **How to observe it:** In the dashboard, select the `Unlimited` strategy on ticker `NOVA` (or test price series `[1, 3, 2, 9]`) and click **Run Backtest**, or execute `python tests/test_runner.py` / `python -m unittest test/test_unlimited.py`.
- **Failure:** The strategy under-reports total gains (yielding $7.00 instead of $9.00 on `[1, 3, 2, 9]`, and $47.00 instead of $59.00 on `NOVA`) and returns status `anomaly` because `if len(pairs) > 1: pairs.pop(0)` arbitrarily drops the initial profitable cycle.
- **Expected:** The strategy retains all identified valley-to-peak swing segments, capturing total cumulative profits ($9.00 on `[1, 3, 2, 9]` and $59.00 on `NOVA`), and returns status `valid`.

### 3. Limited transaction strategy truncates multi-cycle execution path

- **Bug location:** `src/tradesim/strategy/limited.py`, `LimitedTransactionStrategy.run`
- **How to observe it:** In the dashboard, select the `Limited` strategy with `Max transactions` set to `2` and click **Run Backtest**, or execute `python tests/test_runner.py` / `python -m unittest test/test_limited.py`.
- **Failure:** Dynamic programming path reconstruction starts with `chosen = min(1, k)`, truncating the reconstructed schedule to at most one transaction pair, reporting $7.00 instead of $13.00 for $k=2$ on `[2, 8, 1, 8]`, and flagging status as `anomaly`.
- **Expected:** Path reconstruction begins from the configured transaction limit `k`, correctly reconstructing up to `k` optimal transaction pairs ($13.00 for $k=2$ on `[2, 8, 1, 8]`, $10.00 on `[1, 5, 2, 8]`), and returns status `valid`.

### 4. Fee-aware strategy deducts transaction fees twice

- **Bug location:** `src/tradesim/strategy/fee.py`, `FeeStrategy.run`
- **How to observe it:** In the dashboard, select the `Fee` strategy with `Fee per fill` set to `1.00` on price series `[1, 5]` and click **Run Backtest**, or execute `python tests/test_runner.py` / `python -m unittest test/test_fee.py`.
- **Failure:** After `StrategySupport.result()` already accounts for buy and sell fees, `FeeStrategy` recalculates `extra = sum(...)` and subtracts sell fees a second time from net profit and final portfolio value while overriding status to `anomaly`, resulting in an unexpected deficit (reporting $4.00 total fees deducted instead of $2.00).
- **Expected:** Fees are deducted exactly once per order fill (1 buy fee + 1 sell fee = $2.00 total for a round trip), returning $2.00 net profit on `[1, 5]` with status `valid`.

### 5. Cooldown strategy permits premature market re-entry

- **Bug location:** `src/tradesim/strategy/cooldown.py`, `CooldownStrategy.run`
- **How to observe it:** In the dashboard, select the `Cooldown` strategy with `Cooldown days` set to `1` on price series `[1, 5, 2, 8]` and click **Run Backtest**, or execute `python tests/test_runner.py` / `python -m unittest test/test_cooldown.py`.
- **Failure:** The filter condition `if buy < last_sell + rules.cooldown_days:` uses strict inequality `<` instead of `<=`, allowing a buy order on the cooldown boundary day itself (e.g. buying on Day 3 immediately following a Day 2 sale when 1 cooldown day is mandated), and returns status `anomaly`.
- **Expected:** The boundary condition enforces strict non-trading delay (`buy <= last_sell + rules.cooldown_days: continue`), preventing re-entry until the mandatory rest window has elapsed, and returns status `valid`.

### 6. PolicyEngine leaks cumulative fee state across independent backtest runs

- **Bug location:** `src/tradesim/policy/engine.py`, `PolicyEngine.run_backtest`
- **How to observe it:** In the dashboard, run backtests multiple times consecutively on ticker `ACME_TECH` with `Fee per fill` > 0, or execute `python tests/test_runner.py` / `python -m unittest test/test_policy_engine.py`.
- **Failure:** `PolicyEngine` maintains a persistent `self.execution_ledger` across invocations, accumulating past fees and deducting phantom deficits on subsequent runs, degrading reported profit (e.g. initial profit of $41.00 dropping to $29.00 on the third run) and marking results as `anomaly`.
- **Expected:** Backtest executions are completely isolated, idempotent, and state-free between invocations, producing identical and deterministic returns for identical parameter configurations with status `valid`.

## Expected Behaviour After Fixing All Bugs

- Single trade strategy captures the global optimal buy/sell price swing without losing historical minima.
- Unlimited swing trading strategy retains every profitable price swing cycle across market movements.
- Limited transaction strategy reconstructs up to the full configured `k` transaction quota using dynamic programming.
- Fee strategy charges transaction fees exactly once per order fill without double-deduction.
- Cooldown strategy strictly enforces the mandatory rest period between positions before permitting re-entry.
- PolicyEngine maintains complete isolation between backtest runs with zero state leakage across calls.
- The dashboard incident banner updates to healthy ("✓ Backtesting Engine Healthy") and all test suite tests pass.
