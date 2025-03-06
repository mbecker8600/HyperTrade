from __future__ import annotations

from datetime import timedelta
from typing import List, Optional

import pandas as pd
import torch
from loguru import logger
from tensordict import TensorDict, TensorDictBase
from torchrl.data import Bounded, Composite, Unbounded
from torchrl.data.utils import DEVICE_TYPING
from torchrl.envs import EnvBase

from hypertrade.libs.simulator.engine import TradingEngine
from hypertrade.libs.simulator.event.types import EVENT_TYPE
from hypertrade.libs.tsfd.datasets.asset import PricesDataset, TimeSeriesDataset


class TradingEnvironment(EnvBase):
    def __init__(
        self,
        symbols: List[str],
        min_start: pd.Timestamp,
        max_end: pd.Timestamp,
        prices_dataset: PricesDataset,
        feature_dataset: TimeSeriesDataset,
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
            features=Unbounded(
                shape=feature_dataset.observation_shape,
                dtype=torch.float32,  # TODO: refactor so this will stay in sync with the function call
            ),
            shape=(),
        )
        self.min_start = min_start
        self.max_end = max_end
        self.env_type = env_type
        self.max_episode_steps = max_episode_steps
        self.capital_base = capital_base

        self.trading_engine: Optional[TradingEngine] = None
        self.features_dataset = feature_dataset
        self.prices_dataset = prices_dataset
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

        # Take action based on the input tensor
        action = tensordict["action"] / tensordict["action"].sum()
        self.trading_engine.order_manager.place_order_by_weights(
            {
                symbol: float(weight)
                for (symbol, weight) in zip(self.symbols, action[1:])
            }
        )
        original_portfolio_value = (
            self.trading_engine.portfolio_manager.portfolio.portfolio_value
        )
        # Step until desired event (e.g. MARKET_PRE_OPEN)
        self.trading_engine.step_until_event(EVENT_TYPE.PRE_MARKET_OPEN)

        next_portfolio_value = (
            self.trading_engine.portfolio_manager.portfolio.portfolio_value
        )
        # Calculate the reward
        reward = torch.Tensor(
            [
                (next_portfolio_value - original_portfolio_value)
                / original_portfolio_value
            ]
        )

        features = self.features_dataset[
            self.trading_engine.current_time - timedelta(days=1)
        ]

        out = TensorDict(
            {
                "reward": reward,
                "allocations": self._get_portfolio_allocations(),
                "features": features,
                "done": torch.zeros_like(reward, dtype=torch.bool),
            },
            tensordict.shape,
            device=self.device,
        )
        return out

    def _set_seed(self, seed: int) -> None:
        self.rng = torch.Generator(device=self.device).manual_seed(seed)

    # TODO: Implement random portfolio allocations
    # TODO: Implement random start and end dates
    def _reset(self, tensordict: Optional[TensorDictBase] = None) -> TensorDictBase:
        logger.debug("Starting _reset()")

        if tensordict is None or tensordict.is_empty():
            batch_size = self.batch_size
        else:
            batch_size = tensordict.shape

        self.trading_engine = TradingEngine(
            start_time=self.min_start,
            end_time=self.max_end,
            prices_dataset=self.prices_dataset,
            capital_base=self.capital_base,
        )
        self.trading_engine.step_until_event(EVENT_TYPE.PRE_MARKET_OPEN)
        logger.bind(simulation_time=self.trading_engine.current_time).debug(
            "Intialized Trading Engine"
        )

        # FIXME: Should this done automatically? This is because the OHLVC dataset shouldn't
        # include the current day's data
        features = self.features_dataset[
            self.trading_engine.current_time - timedelta(days=1)
        ]

        out = TensorDict(
            {
                "allocations": self._get_portfolio_allocations(),
                "features": features,
            },
            batch_size,
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
