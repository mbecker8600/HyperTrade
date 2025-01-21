from __future__ import annotations


from typing import Dict, Optional, Any

import torch
from tensordict import TensorDict, TensorDictBase
from torchrl.data import Categorical, Composite, NonTensor, Unbounded

from torchrl.envs import EnvBase

from torchrl.envs.utils import _classproperty


class TradingEnvironment(EnvBase):
    pass
    # def __init__(self, td_params: Optional[TensorDict] = None, seed: Optional[int] = None, device: str = "cpu") -> None:
    #     if td_params is None:
    #         td_params = self.gen_params()

    #     super().__init__(device=device, batch_size=[])
    #     self._make_spec(td_params)
    #     if seed is None:
    #         seed = torch.empty((), dtype=torch.int64).random_().item()
    #     self.set_seed(seed)

    # # Helpers: _make_step and gen_params
    # gen_params = staticmethod(gen_params)
    # _make_spec = _make_spec

    # # Mandatory methods: _step, _reset and _set_seed
    # _reset = _reset
    # _step = staticmethod(_step)
    # _set_seed = _set_seed
