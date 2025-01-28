import unittest

import pandas as pd

from hypertrade.libs.logging.setup import initialize_logging
from hypertrade.libs.simulator.financials.performance import PerformanceTracker
from hypertrade.libs.simulator.financials.portfolio import Portfolio

# import hypertrade.libs.debugging  # donotcommit


class TestPerformanceTracker(unittest.TestCase):

    def setUp(self) -> None:
        self.performance_tracker = PerformanceTracker()
        self.portfolio = Portfolio(
            capital_base=1000.0,
        )
        data = [
            [
                "GE",
                pd.Timestamp("2018-12-31 09:30:00"),
                1,
                35.37,
            ],
            [
                "GE",
                pd.Timestamp("2018-12-28 16:00:00"),
                1,
                35.33,
            ],
            [
                "BA",
                pd.Timestamp("2018-12-10 16:00:00"),
                1,
                317.13,
            ],
        ]

        self.portfolio.positions = pd.DataFrame(
            data,
            columns=["symbol", "dt", "amount", "cost_basis"],
        )
        self.portfolio.positions.set_index(["symbol", "dt"], inplace=True)

    def test_performance_tracker_initialization(self) -> None:
        """Basic initialization of the PerformanceTracker object"""
        self.assertEqual(self.performance_tracker.daily_returns.empty, True)
        self.assertEqual(self.performance_tracker.daily_positions.empty, True)
        self.assertEqual(self.performance_tracker._previous_portfolio, None)

    def test_first_day_record_daily_metrics(self) -> None:
        """First day recording metrics shouldn't record daily returns"""

        self.portfolio.current_market_prices = pd.Series(
            {
                "GE": 35.37,
                "BA": 317.13,
            }
        )

        self.performance_tracker.record_daily_metrics(
            date=pd.Timestamp("2019-01-01"), portfolio=self.portfolio
        )
        self.assertEqual(
            self.performance_tracker.daily_positions.loc[pd.Timestamp("2019-01-01")][
                "BA"
            ],
            1,
        )
        self.assertEqual(
            self.performance_tracker.daily_positions.loc[pd.Timestamp("2019-01-01")][
                "GE"
            ],
            2,
        )
        self.assertTrue(self.performance_tracker.daily_returns.empty)

    def test_second_record_daily_metrics(self) -> None:

        self.portfolio.current_market_prices = pd.Series(
            {
                "GE": 35.37,
                "BA": 317.13,
            }
        )
        self.performance_tracker.record_daily_metrics(
            date=pd.Timestamp("2019-01-01"), portfolio=self.portfolio
        )
        self.portfolio.current_market_prices = pd.Series(
            {
                "GE": 36.37,
                "BA": 318.13,
            }
        )
        self.performance_tracker.record_daily_metrics(
            date=pd.Timestamp("2019-01-02"), portfolio=self.portfolio
        )
        self.assertAlmostEqual(
            self.performance_tracker.daily_returns.loc[pd.Timestamp("2019-01-02")],
            0.00216,
            places=4,
        )


if __name__ == "__main__":
    initialize_logging(level="DEBUG")
    unittest.main()
