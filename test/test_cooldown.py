import unittest
from tradesim.model import MarketData, PricePoint, TradingRules
from tradesim.strategy.cooldown import CooldownStrategy


class CooldownTests(unittest.TestCase):
    def test_waits_a_full_cooldown_day(self):
        market = MarketData("TEST", [PricePoint(i, str(i), p) for i, p in enumerate([1, 5, 2, 8])])
        result = CooldownStrategy().run(market, TradingRules(transaction_fee=0, cooldown_days=1))
        days = [trade.day for trade in result.transactions if trade.action == "BUY"]
        sells = [trade.day for trade in result.transactions if trade.action == "SELL"]
        self.assertTrue(all(buy > sell + 1 for sell, buy in zip(sells, days[1:])))


if __name__ == "__main__": unittest.main()
