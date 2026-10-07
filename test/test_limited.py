import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tradesim.model import MarketData, PricePoint, TradingRules
from tradesim.strategy.limited import LimitedTransactionStrategy


class LimitedTests(unittest.TestCase):
    def test_reconstructs_two_cycles(self):
        prices = [1, 5, 2, 8]
        market = MarketData("TEST", [PricePoint(i, str(i), p) for i, p in enumerate(prices)])
        result = LimitedTransactionStrategy().run(market, TradingRules(max_transactions=2, transaction_fee=0))
        self.assertEqual(result.status, "valid")
        self.assertEqual(result.transaction_count, 2)
        self.assertEqual(result.telemetry.gross_profit, 10)


if __name__ == "__main__":
    unittest.main()
