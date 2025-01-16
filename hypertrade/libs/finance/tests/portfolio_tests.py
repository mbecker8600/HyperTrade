import unittest

from hypertrade.libs.finance.assets import Asset
from hypertrade.libs.finance.portfolio import Portfolio, Position


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

    def test_portfolio_current_portfolio_weights_single_asset(self) -> None:
        """Basic initialization of the Portfolio object"""
        portfolio = Portfolio(capital_base=1000.0)

        google_asset = Asset(
            sid=1, symbol="GOOGL", asset_name="Google", price_multiplier=1.0
        )
        google_position = Position(
            asset=google_asset,
            amount=10,
            cost_basis=1000.0,
            last_sale_price=100.0,
            last_sale_date="2021-01-01",
        )

        portfolio.positions[google_asset] = google_position
        portfolio.positions_value = 1000.0

        weights = portfolio.current_portfolio_weights
        self.assertEqual(weights[google_asset], 1.0)


if __name__ == "__main__":
    unittest.main()
