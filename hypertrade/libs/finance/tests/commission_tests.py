import unittest

from hypertrade.libs.finance.commission import NoCommission


class TestNoCommisionModel(unittest.TestCase):

    def test_no_commision_returns_zero(self) -> None:
        """NoCommission Commision Model should return zero for all trades"""

        self.assertEqual(NoCommission.calculate(None, None), 0.0)
