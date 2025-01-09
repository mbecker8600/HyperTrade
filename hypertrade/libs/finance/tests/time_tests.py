import unittest
from datetime import datetime
from hypertrade.libs.finance.time import TradingClock


class TestTradingClock(unittest.TestCase):

    def test_daily_iteration(self) -> None:
        """Basic initialization of the Portfolio object"""
        clock = TradingClock(start_time=datetime(
            2001, 1, 1), end_time=datetime(2001, 1, 5))

        self.assertEqual(next(clock), datetime(2001, 1, 2))


if __name__ == "__main__":
    unittest.main()
