import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tradesim.data import MarketDataRepository
from tradesim.model import MarketData, PricePoint, TradingRules
from tradesim.strategy.single_trade import SingleTradeStrategy


class SingleTradeTests(unittest.TestCase):
    def test_finds_best_buy_before_sell(self):
        market = MarketData("TEST", [PricePoint(i, f"2025-01-0{i+1}", p) for i, p in enumerate([3, 1, 8])])
        result = SingleTradeStrategy().run(market, TradingRules(transaction_fee=0))
        self.assertEqual(result.status, "valid")
        self.assertEqual(result.telemetry.gross_profit, 7)


if __name__ == "__main__":
    unittest.main()
