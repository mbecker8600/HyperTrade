

import pandas as pd


class BacktestEngine():

    def __init__(self, start_date: pd.Timestamp = None, capital_base: float = 0.0) -> None:
        self.cash_flow = 0.0
        self.starting_cash = capital_base
        self.portfolio_value = capital_base
        self.pnl = 0.0
        self.returns = 0.0
        self.cash = capital_base
        self.positions: Positions = {}
        self.start_date = start_date
        self.positions_value = 0.0
        self.positions_exposure = 0.0

    def run_backtest(self) -> None:
        print("Running backtest")
