from __future__ import annotations

import os
from typing import List, Optional

import exchange_calendars as xcals
import pandas as pd
import torch
from loguru import logger
from tensordict import TensorDict, TensorDictBase
from torchrl.data import Bounded, Composite, Unbounded
from torchrl.data.utils import DEVICE_TYPING
from torchrl.envs import EnvBase

from hypertrade.libs.simulator.engine import TradingEngine
from hypertrade.libs.simulator.event.types import EVENT_TYPE
from hypertrade.libs.tsfd.datasets.asset import PricesDataset
from hypertrade.libs.tsfd.sources.csv import CSVSource
from hypertrade.libs.tsfd.sources.formats.ohlvc import OHLVCDataSourceFormat


# trunk-ignore-all(mypy,ruff,pyright)
class TradingEnvironment(EnvBase):
    def __init__(
        self,
        symbols: List[str],
        min_start: pd.Timestamp,
        max_end: pd.Timestamp,
        env_type: str = "train",
        max_episode_steps: Optional[int] = None,
        capital_base: int = 100000,
        device: DEVICE_TYPING = "cpu",
    ) -> None:
        super().__init__(device=device, batch_size=[])
        self.symbols = symbols
        self.rng: Optional[torch.Generator] = None
        self.observation_spec: Composite = Composite(
            allocations=Unbounded(shape=len(self.symbols), dtype=torch.float32),
            historical_rolling_averages=Unbounded(
                shape=len(self.symbols * 2 * 4),
                dtype=torch.float32,  # TODO: refactor so this will stay in sync with the function call
            ),
            shape=(),
        )
        self.min_start = min_start
        self.max_end = max_end
        self.env_type = env_type
        self.max_episode_steps = max_episode_steps
        self.capital_base = capital_base

        # FIXME: This is a hack to get the testing data, but should clean this up.
        # Use sample data for testing
        ws = os.path.dirname(__file__)
        sample_data_path = os.path.join(
            ws, "../../libs/simulator/data/tests/data/ohlvc/sample.csv"
        )

        # Create an OCHLV data source using a CSV file
        cal = xcals.get_calendar("XNYS")
        self.ohlvc_dataset = PricesDataset(
            data_source=OHLVCDataSourceFormat(
                CSVSource(source=sample_data_path),
            ),
            name="prices",
            trading_calendar=cal,
        )

        self.trading_engine: Optional[TradingEngine] = None

        self.state_spec = self.full_observation_spec.clone()

        self.action_spec: Bounded = Bounded(
            maximum=1.0,
            minimum=0.0,
            shape=(1 + len(self.symbols),),  # the first entry will be cash
            dtype=torch.float32,
        )

        reward_spec = Unbounded(shape=1)
        self.reward_spec = reward_spec.expand([*self.batch_size, *reward_spec.shape])

    def _step(self, tensordict: TensorDictBase) -> TensorDictBase:
        logger.bind(simulation_time=self.trading_engine.current_time).debug(
            "Starting _step()"
        )
        # Step until desired event (e.g. MARKET_PRE_OPEN)
        next_event = self.trading_engine.step_until_event(EVENT_TYPE.PRE_MARKET_OPEN)

        tensordict["action"]

        out = TensorDict(
            {
                "reward": reward,
                "allocations": self._get_portfolio_allocations(),
                "historical_rolling_averages": historical_rolling_averages,
                "done": done,
            },
            tensordict.shape,
            device=self.device,
        )
        return out

    def _set_seed(self, seed: int) -> None:
        self.rng = torch.Generator(device=self.device).manual_seed(seed)

    def _reset(self, tensordict: TensorDictBase) -> TensorDictBase:
        logger.debug("Starting _reset()")
        # TODO: Randomize the start/end dates for engine when restarting
        self.trading_engine = TradingEngine(
            start_time=self.min_start,
            end_time=self.max_end,
            prices_dataset=self.ohlvc_dataset,
            capital_base=self.capital_base,
        )
        self.trading_engine.step_until_event(EVENT_TYPE.PRE_MARKET_OPEN)
        logger.bind(simulation_time=self.trading_engine.current_time).debug(
            "Intialized Trading Engine"
        )

        out = TensorDict(
            {
                "allocations": self._get_portfolio_allocations(),
                "historical_rolling_averages": historical_rolling_averages,
            },
            tensordict.shape,
            device=self.device,
        )
        return out

    def _get_portfolio_allocations(self) -> torch.Tensor:
        """
        Returns the current portfolio allocations as a tensor and ensures they are padded
        with zeros for any missing symbols.
        """
        return torch.from_numpy(
            pd.Series(None, index=self.symbols)
            .add(
                self.trading_engine.portfolio_manager.portfolio.current_portfolio_weights
            )
            .fillna(0)
            .values
        )
