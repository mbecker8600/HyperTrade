# Description: Utility functions for RL training
from typing import Tuple

import pandas as pd
import torch
from omegaconf import DictConfig
from torch import nn, optim
from torchrl.collectors import MultiSyncDataCollector, SyncDataCollector
from torchrl.collectors.collectors import DataCollectorBase
from torchrl.data import TensorDictPrioritizedReplayBuffer, TensorDictReplayBuffer
from torchrl.data.replay_buffers import ReplayBuffer
from torchrl.data.replay_buffers.storages import LazyMemmapStorage
from torchrl.data.utils import DEVICE_TYPING
from torchrl.envs import (
    CatTensors,
    Compose,
    DoubleToFloat,
    EnvBase,
    EnvCreator,
    InitTracker,
    ParallelEnv,
    RewardClipping,
    RewardScaling,
    RewardSum,
    StepCounter,
    TransformedEnv,
)
from torchrl.envs.utils import ExplorationType, set_exploration_type
from torchrl.modules import (
    MLP,
    AdditiveGaussianWrapper,
    OrnsteinUhlenbeckProcessWrapper,
    SafeModule,
    SafeSequential,
    TanhModule,
    ValueOperator,
)
from torchrl.objectives import LossModule, SoftUpdate
from torchrl.objectives.ddpg import DDPGLoss
from torchrl.objectives.utils import TargetNetUpdater, ValueEstimators

from hypertrade.ai.rl.env import TradingEnvironment

# ====================================================================
# Environment utils
# -----------------


# trunk-ignore-all(mypy,pyright)
def env_maker(cfg: DictConfig, env_type: str) -> EnvBase:
    symbol_file = cfg.portfolio.symbol_file
    symbols_df = pd.read_csv(symbol_file, header=0)
    device = cfg.env.device
    if env_type == "train":
        start = pd.Timestamp(cfg.env.training_start)
        end = pd.Timestamp(cfg.env.training_end)
        return TradingEnvironment(
            symbols=symbols_df.symbol.to_list(),
            min_start=start,
            max_end=end,
            env_type=env_type,
            max_episode_steps=cfg.env.max_episode_steps,
            device=device,
        )
    elif env_type == "eval":
        start = pd.Timestamp(cfg.env.eval_start)
        end = pd.Timestamp(cfg.env.eval_end)
        return TradingEnvironment(
            symbols=symbols_df.symbol.to_list(),
            min_start=start,
            max_end=end,
            env_type=env_type,
            device=device,
        )
    else:
        raise NotImplementedError


def apply_env_transforms(env: EnvBase, cfg: DictConfig) -> EnvBase:

    max_episode_steps = cfg.env.max_episode_steps

    transforms = [
        InitTracker(),
        StepCounter(max_episode_steps),
        DoubleToFloat(),
        RewardSum(),
        # ObservationNorm(standard_normal=True, in_keys=["allocations"]),
        CatTensors(
            in_keys=["allocations", "historical_rolling_averages"],
            out_key="observation",
        ),
    ]

    if cfg.env.transforms.reward_scaling is not None:
        transforms.append(
            RewardScaling(
                loc=cfg.env.transforms.reward_scaling.loc,
                scale=cfg.env.transforms.reward_scaling.scale,
            )
        )

    if cfg.env.transforms.reward_clipping is not None:
        transforms.append(
            RewardClipping(
                clamp_min=cfg.env.transforms.reward_clipping.min,
                clamp_max=cfg.env.transforms.reward_clipping.max,
            )
        )

    transformed_env = TransformedEnv(
        env,
        Compose(*transforms),
    )
    return transformed_env


def make_environment(cfg: DictConfig) -> Tuple[EnvBase, EnvBase]:
    """Make environments for training and evaluation."""

    # # If there is only one environment per collector, no need for parallelism
    # if cfg.collector.env_per_collector == 1:
    #     train_env = EnvCreator(
    #         lambda cfg=cfg: apply_env_transforms(env_maker(cfg, type="train")),
    #         create_env_kwargs={"cfg": cfg},
    #     )

    #     eval_env = EnvCreator(
    #         lambda cfg=cfg: apply_env_transforms(env_maker(cfg, type="eval")),
    #         create_env_kwargs={"cfg": cfg},
    #     )
    #     return train_env, eval_env

    # Create parallel environments
    parallel_env = ParallelEnv(
        num_workers=cfg.collector.env_per_collector,
        create_env_fn=EnvCreator(lambda cfg=cfg: env_maker(cfg, env_type="train")),
        serial_for_single=True,
        device=cfg.env.device,
    )
    parallel_env.set_seed(cfg.env.seed)

    train_env = apply_env_transforms(parallel_env, cfg)
    # train_env.transform[4].init_stats(
    #     num_iter=1000, reduce_dim=dim
    # )  # initialize stats for observation norm

    eval_env = TransformedEnv(
        ParallelEnv(
            cfg.collector.env_per_collector,
            EnvCreator(lambda cfg=cfg: env_maker(cfg, env_type="eval")),
            serial_for_single=True,
            device=cfg.env.device,
        ),
        train_env.transform.clone(),
    )
    return train_env, eval_env


# ====================================================================
# Collector and replay buffer
# ---------------------------


def make_collector(
    cfg: DictConfig,
    train_env: EnvBase,
    actor_model_explore: OrnsteinUhlenbeckProcessWrapper | AdditiveGaussianWrapper,
) -> DataCollectorBase:
    """Make collector."""
    if cfg.collector.n_collectors == 1:
        collector = SyncDataCollector(
            train_env,
            actor_model_explore,
            frames_per_batch=cfg.collector.frames_per_batch,
            init_random_frames=cfg.collector.init_random_frames,
            reset_at_each_iter=cfg.collector.reset_at_each_iter,
            total_frames=cfg.collector.total_frames,
            device=cfg.collector.device,
        )
    else:
        collector = MultiSyncDataCollector(
            [train_env for _ in range(cfg.collector.n_collectors)],
            actor_model_explore,
            frames_per_batch=cfg.collector.frames_per_batch,
            init_random_frames=cfg.collector.init_random_frames,
            reset_at_each_iter=cfg.collector.reset_at_each_iter,
            total_frames=cfg.collector.total_frames,
            device=cfg.collector.device,
        )
    collector.set_seed(cfg.env.seed)
    return collector


def make_replay_buffer(
    batch_size: int,
    prb: bool = False,
    buffer_size: int = 1000000,
    scratch_dir=None,
    device: DEVICE_TYPING = "cpu",
    prefetch: int = 2,
) -> ReplayBuffer:
    if prb:
        replay_buffer = TensorDictPrioritizedReplayBuffer(
            alpha=0.7,
            beta=0.5,
            pin_memory=False,
            prefetch=prefetch,
            storage=LazyMemmapStorage(
                buffer_size,
                scratch_dir=scratch_dir,
                device=device,
            ),
            batch_size=batch_size,
        )
    else:
        replay_buffer = TensorDictReplayBuffer(
            pin_memory=False,
            prefetch=prefetch,
            storage=LazyMemmapStorage(
                buffer_size,
                scratch_dir=scratch_dir,
                device=device,
            ),
            batch_size=batch_size,
        )
    return replay_buffer


# ====================================================================
# Model
# -----


def make_ddpg_agent(cfg: DictConfig, train_env, eval_env, device):
    """Make DDPG agent."""
    # Define Actor Network
    in_keys = ["observation"]
    action_spec = train_env.action_spec
    if train_env.batch_size:
        action_spec = action_spec[(0,) * len(train_env.batch_size)]
    actor_net_kwargs = {
        "num_cells": cfg.network.hidden_sizes,
        "out_features": action_spec.shape[-1],
        "activation_class": get_activation(cfg),
    }

    actor_net = MLP(**actor_net_kwargs)

    in_keys_actor = in_keys
    actor_module = SafeModule(
        actor_net,
        in_keys=in_keys_actor,
        out_keys=[
            "param",
        ],
    )
    actor = SafeSequential(
        actor_module,
        TanhModule(
            in_keys=["param"],
            out_keys=["action"],
            spec=action_spec,
        ),
    )

    # Define Critic Network
    qvalue_net_kwargs = {
        "num_cells": cfg.network.hidden_sizes,
        "out_features": 1,
        "activation_class": get_activation(cfg),
    }

    qvalue_net = MLP(
        **qvalue_net_kwargs,
    )

    qvalue = ValueOperator(
        in_keys=["action"] + in_keys,
        module=qvalue_net,
    )

    model: nn.ModuleList = nn.ModuleList([actor, qvalue]).to(device)

    # init nets
    with torch.no_grad(), set_exploration_type(ExplorationType.RANDOM):
        td = eval_env.reset()
        td = td.to(device)
        for net in model:
            net(td)
    del td
    eval_env.close()

    # Exploration wrappers:
    if cfg.network.noise_type == "ou":
        actor_model_explore = OrnsteinUhlenbeckProcessWrapper(
            model[0],
            annealing_num_steps=cfg.network.annealing_num_steps,
        ).to(device)
    elif cfg.network.noise_type == "gaussian":
        actor_model_explore = AdditiveGaussianWrapper(
            model[0],
            sigma_end=1.0,
            sigma_init=1.0,
            mean=0.0,
            std=0.1,
        ).to(device)
    else:
        raise NotImplementedError

    return model, actor_model_explore


# ====================================================================
# DDPG Loss
# ---------


def make_loss_module(cfg: DictConfig, model) -> Tuple[LossModule, TargetNetUpdater]:
    """Make loss module and target network updater."""
    # Create DDPG loss
    loss_module = DDPGLoss(
        actor_network=model[0],
        value_network=model[1],
        loss_function=cfg.optim.loss_function,
        delay_actor=True,
        delay_value=True,
    )
    if cfg.optim.value_estimator == "GAE":
        loss_module.make_value_estimator(
            value_type=ValueEstimators.GAE, gamma=cfg.optim.gamma, lmbda=cfg.optim.lmbda
        )
    elif cfg.optim.value_estimator == "TD0":
        loss_module.make_value_estimator(
            value_type=ValueEstimators.TD0, gamma=cfg.optim.gamma
        )
    elif cfg.optim.value_estimator == "TD1":
        loss_module.make_value_estimator(
            value_type=ValueEstimators.TD1, gamma=cfg.optim.gamma
        )
    elif cfg.optim.value_estimator == "TDLambda":
        loss_module.make_value_estimator(
            value_type=ValueEstimators.TDLambda,
            gamma=cfg.optim.gamma,
            lmbda=cfg.optim.lmbda,
        )

    # Define Target Network Updater
    target_net_updater = SoftUpdate(loss_module, eps=cfg.optim.target_update_polyak)
    return loss_module, target_net_updater


def make_optimizer(cfg: DictConfig, loss_module):
    critic_params = list(loss_module.value_network_params.flatten_keys().values())
    actor_params = list(loss_module.actor_network_params.flatten_keys().values())

    optimizer_actor = optim.Adam(
        actor_params, lr=cfg.optim.actor_lr, weight_decay=cfg.optim.actor_weight_decay
    )
    optimizer_critic = optim.Adam(
        critic_params,
        lr=cfg.optim.critic_lr,
        weight_decay=cfg.optim.critic_weight_decay,
    )
    return optimizer_actor, optimizer_critic


# ====================================================================
# General utils
# ---------


def log_metrics(logger, metrics, step):
    for metric_name, metric_value in metrics.items():
        logger.log_scalar(metric_name, metric_value, step)


def get_activation(cfg):
    if cfg.network.activation == "relu":
        return nn.ReLU
    elif cfg.network.activation == "tanh":
        return nn.Tanh
    elif cfg.network.activation == "leaky_relu":
        return nn.LeakyReLU
    else:
        raise NotImplementedError
