import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tradesim.model import TradingRules
from tradesim.policy import PolicyEngine


class PolicyEngineTests(unittest.TestCase):
    def test_runs_are_isolated(self):
        engine = PolicyEngine()
        rules = TradingRules(max_transactions=2, transaction_fee=2, cooldown_days=1)
        first = engine.run_backtest("ACME_TECH", "combined", rules)
        engine.run_backtest("NOVA", "combined", rules)
        third = engine.run_backtest("ACME_TECH", "combined", rules)
        self.assertEqual(first.status, "valid")
        self.assertEqual(third.status, "valid")
        self.assertEqual(first.total_profit, third.total_profit)


if __name__ == "__main__":
    unittest.main()
