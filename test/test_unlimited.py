import unittest
from tradesim.data import MarketDataRepository
from tradesim.model import TradingRules
from tradesim.strategy.unlimited import UnlimitedStrategy


class UnlimitedTests(unittest.TestCase):
    def test_keeps_each_profitable_cycle(self):
        result = UnlimitedStrategy().run(MarketDataRepository().get("NOVA"), TradingRules(transaction_fee=0))
        self.assertEqual(result.telemetry.gross_profit, 59)


if __name__ == "__main__": unittest.main()
