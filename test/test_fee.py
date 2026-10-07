import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tradesim.model import MarketData, PricePoint, TradingRules
from tradesim.strategy.fee import FeeStrategy


class FeeTests(unittest.TestCase):
    def test_deducts_fee_once_per_fill(self):
        market = MarketData("TEST", [PricePoint(i, str(i), p) for i, p in enumerate([1, 5])])
        result = FeeStrategy().run(market, TradingRules(transaction_fee=1))
        self.assertEqual(result.status, "valid")
        self.assertEqual(result.telemetry.fees_paid, 2)
        self.assertEqual(result.total_profit, 2)


if __name__ == "__main__":
    unittest.main()
