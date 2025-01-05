import unittest

# import hypertrade.libs.debugging

from hypertrade.libs.finance.accounting import Portfolio


class TestPortfolio(unittest.TestCase):

    def test_portfolio_initialization(self) -> None:
        """Basic initialization of the Portfolio object"""
        portfolio = Portfolio(capital_base=1000.0)
        self.assertEqual(portfolio.starting_cash, 1000.0)
        self.assertEqual(portfolio.cash, 1000.0)
        self.assertEqual(portfolio.portfolio_value, 1000.0)
        self.assertEqual(portfolio.pnl, 0.0)
        self.assertEqual(portfolio.returns, 0.0)
        self.assertEqual(portfolio.positions, {})
        self.assertEqual(portfolio.positions_value, 0.0)
        self.assertEqual(portfolio.positions_exposure, 0.0)
        self.assertEqual(portfolio.cash_flow, 0.0)
        self.assertIsNone(portfolio.start_date)
        self.assertEqual(portfolio.capital_used, 0.0)

        weights = portfolio.current_portfolio_weights
        self.assertTrue(weights.empty)

    def test_portfolio_current_portfolio_weights(self) -> None:
        """Basic initialization of the Portfolio object"""
        portfolio = Portfolio(capital_base=1000.0)


if __name__ == "__main__":
    unittest.main()
