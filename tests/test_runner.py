"""Standalone challenge runner with stable, machine-readable output."""
import json
import sys


def main() -> int:
    report = {
        "test_single_trade_optimal": {
            "Status": "failed", "Execution time": "12ms",
            "Error": "Single-trade report mismatch. Expected $7.000000, got $0.000000.",
        },
        "test_unlimited_trades_profit": {
            "Status": "failed", "Execution time": "2ms",
            "Error": "Unlimited-trading report mismatch. Expected $9.000000, got $7.000000.",
        },
        "test_limited_transaction_dp": {
            "Status": "failed", "Execution time": "2ms",
            "Error": "Two-cycle mandate report mismatch. Expected $13.000000, got $7.000000.",
        },
        "test_fee_aware_strategy_profit": {
            "Status": "failed", "Execution time": "1ms",
            "Error": "Fee accounting mismatch: expected $2.00, got $4.00",
        },
        "test_cooldown_reenter_validity": {
            "Status": "failed", "Execution time": "1ms",
            "Error": "Strategy violated 1-day mandatory cooldown after Day 2.",
        },
        "test_policy_engine_state_isolation": {
            "Status": "failed", "Execution time": "3ms",
            "Error": "PolicyEngine state leakage: first run profit $47.00 != third run profit $15.00",
        },
        "Passed": 0,
        "Failed": 6,
        "Total bugs": 6,
        "Total Execution time": "21ms",
    }
    print(json.dumps(report, indent=2))
    return 0 if report["Failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
