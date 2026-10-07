"""Standalone challenge runner with dynamic test execution and strict JSON protocol."""
import json
import sys
import time
from pathlib import Path

# Ensure 'src' is accessible without requiring manual PYTHONPATH configuration
root = Path(__file__).resolve().parents[1]
src_dir = str(root / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from tradesim.data import MarketDataRepository
from tradesim.model import MarketData, PricePoint, TradingRules
from tradesim.strategy import (
    SingleTradeStrategy,
    UnlimitedStrategy,
    LimitedTransactionStrategy,
    FeeStrategy,
    CooldownStrategy,
)
from tradesim.policy import PolicyEngine


def test_single_trade_optimal() -> None:
    market = MarketData("TEST", [PricePoint(i, f"2025-01-0{i+1}", p) for i, p in enumerate([3, 1, 8])])
    result = SingleTradeStrategy().run(market, TradingRules(transaction_fee=0))
    if result.status != "valid" or result.telemetry.gross_profit != 7.0:
        raise AssertionError(
            f"Single-trade report mismatch. Expected $7.000000, got ${result.telemetry.gross_profit:.6f}."
        )


def test_unlimited_trades_profit() -> None:
    market = MarketData("TEST", [PricePoint(i, str(i), p) for i, p in enumerate([1, 3, 2, 9])])
    result = UnlimitedStrategy().run(market, TradingRules(transaction_fee=0))
    if result.status != "valid" or result.telemetry.gross_profit != 9.0:
        raise AssertionError(
            f"Unlimited-trading report mismatch. Expected $9.000000, got ${result.telemetry.gross_profit:.6f}."
        )


def test_limited_transaction_dp() -> None:
    market = MarketData("TEST", [PricePoint(i, str(i), p) for i, p in enumerate([2, 8, 1, 8])])
    result = LimitedTransactionStrategy().run(market, TradingRules(max_transactions=2, transaction_fee=0))
    if result.status != "valid" or result.transaction_count != 2 or result.telemetry.gross_profit != 13.0:
        raise AssertionError(
            f"Two-cycle mandate report mismatch. Expected $13.000000, got ${result.telemetry.gross_profit:.6f}."
        )


def test_fee_aware_strategy_profit() -> None:
    market = MarketData("TEST", [PricePoint(i, str(i), p) for i, p in enumerate([1, 5])])
    result = FeeStrategy().run(market, TradingRules(transaction_fee=1.0))
    if result.status != "valid":
        raise AssertionError("Fee accounting mismatch: expected $2.00, got $4.00 (status: anomaly)")
    if result.total_profit != 2.0 or result.telemetry.fees_paid != 2.0:
        raise AssertionError(f"Fee accounting mismatch: expected $2.00, got ${result.total_profit:.2f}")


def test_cooldown_reenter_validity() -> None:
    market = MarketData("TEST", [PricePoint(i, str(i), p) for i, p in enumerate([1, 5, 2, 8])])
    result = CooldownStrategy().run(market, TradingRules(transaction_fee=0, cooldown_days=1))
    days = [trade.day for trade in result.transactions if trade.action == "BUY"]
    sells = [trade.day for trade in result.transactions if trade.action == "SELL"]
    for sell, buy in zip(sells, days[1:]):
        if buy <= sell + 1:
            raise AssertionError(f"Strategy violated 1-day mandatory cooldown after Day {sell + 1}.")
    if result.status != "valid":
        raise AssertionError(f"CooldownStrategy returned status '{result.status}', expected 'valid'.")


def test_policy_engine_state_isolation() -> None:
    engine = PolicyEngine()
    rules = TradingRules(max_transactions=2, transaction_fee=2.0, cooldown_days=1)
    first = engine.run_backtest("ACME_TECH", "combined", rules)
    engine.run_backtest("NOVA", "combined", rules)
    third = engine.run_backtest("ACME_TECH", "combined", rules)
    if first.total_profit != third.total_profit:
        raise AssertionError(
            f"PolicyEngine state leakage: first run profit ${first.total_profit:.2f} != third run profit ${third.total_profit:.2f}"
        )
    if first.status != "valid" or third.status != "valid":
        raise AssertionError(f"PolicyEngine returned non-valid status: first='{first.status}', third='{third.status}'.")


def main() -> int:
    test_suite = [
        ("test_single_trade_optimal", test_single_trade_optimal),
        ("test_unlimited_trades_profit", test_unlimited_trades_profit),
        ("test_limited_transaction_dp", test_limited_transaction_dp),
        ("test_fee_aware_strategy_profit", test_fee_aware_strategy_profit),
        ("test_cooldown_reenter_validity", test_cooldown_reenter_validity),
        ("test_policy_engine_state_isolation", test_policy_engine_state_isolation),
    ]

    report = {}
    passed = 0
    failed = 0
    total_start = time.perf_counter()

    for name, test_fn in test_suite:
        start_time = time.perf_counter()
        try:
            test_fn()
            elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))
            report[name] = {
                "Status": "passed",
                "Execution time": f"{elapsed_ms}ms",
            }
            passed += 1
        except Exception as e:
            elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))
            report[name] = {
                "Status": "failed",
                "Execution time": f"{elapsed_ms}ms",
                "Error": str(e),
            }
            failed += 1

    total_elapsed_ms = max(1, int((time.perf_counter() - total_start) * 1000))
    report["Passed"] = passed
    report["Failed"] = failed
    report["Total bugs"] = len(test_suite)
    report["Total Execution time"] = f"{total_elapsed_ms}ms"

    print(json.dumps(report, indent=2))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
