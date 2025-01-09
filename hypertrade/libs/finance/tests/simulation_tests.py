import unittest
from datetime import datetime
from hypertrade.libs.finance.order import Order
from hypertrade.libs.finance.simulation import SimulationState, Simulator

# import hypertrade.libs.debugging  # donotcommit


class TestSimulator(unittest.TestCase):

    def test_basic_simulation(self) -> None:
        """Basic initialization of the Portfolio object"""
        simulator = Simulator(start_time=datetime(
            2001, 1, 1), end_time=datetime(2001, 1, 5))

        state: SimulationState
        for state in simulator:
            # Look at state, make decisions
            current_google_price = state.current_prices.loc["GOOGL"]
            # actions = strategy.run(state)
            # # Place orders
            # orders = [Order()]
            # simulator.place_orders(orders)


if __name__ == "__main__":
    unittest.main()
