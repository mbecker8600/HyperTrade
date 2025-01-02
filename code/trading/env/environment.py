from __future__ import annotations


from typing import Dict, Optional

import torch
from tensordict import TensorDict, TensorDictBase
from torchrl.data import Categorical, Composite, NonTensor, Unbounded

from torchrl.envs import EnvBase

from torchrl.envs.utils import _classproperty


class TradingEnvironment(EnvBase):
    _hash_table: Dict[int, str] = {}

    def __init__(self, stateful: bool = False):
        pass

    def rand_action(self, tensordict: Optional[TensorDictBase] = None) -> TensorDict:
        self._set_action_space(tensordict)
        return super().rand_action(tensordict)

    def _is_done(self, board):
        return board.is_game_over() | board.is_fifty_moves()

    def _reset(self, tensordict=None):
        fen = None
        if tensordict is not None:
            fen = self._get_fen(tensordict).data
            dest = tensordict.empty()
        else:
            dest = TensorDict()

        if fen is None:
            self.board.reset()
            fen = self.board.fen()
        else:
            self.board.set_fen(fen)
            if self._is_done(self.board):
                raise ValueError(
                    "Cannot reset to a fen that is a gameover state." f" fen: {fen}"
                )

        hashing = hash(fen)

        self._set_action_space()
        turn = self.board.turn
        return dest.set("fen", fen).set("hashing", hashing).set("turn", turn)

    def _set_action_space(self, tensordict: TensorDict | None = None):
        if not self.stateful and tensordict is not None:
            fen = self._get_fen(tensordict).data
            self.board.set_fen(fen)
        self.action_spec.set_provisional_n(self.board.legal_moves.count())

    @classmethod
    def _get_fen(cls, tensordict):
        fen = tensordict.get("fen", None)
        if fen is None:
            hashing = tensordict.get("hashing", None)
            if hashing is not None:
                fen = cls._hash_table.get(hashing.item())
        return fen

    def get_legal_moves(self, tensordict=None, uci=False):
        """List the legal moves in a position.

        To choose one of the actions, the "action" key can be set to the index
        of the move in this list.

        Args:
            tensordict (TensorDict, optional): Tensordict containing the fen
                string of a position. Required if not stateful. If stateful,
                this argument is ignored and the current state of the env is
                used instead.

            uci (bool, optional): If ``False``, moves are given in SAN format.
                If ``True``, moves are given in UCI format. Default is
                ``False``.

        """
        board = self.board
        if not self.stateful:
            if tensordict is None:
                raise ValueError(
                    "tensordict must be given since this env is not stateful"
                )
            fen = self._get_fen(tensordict).data
            board.set_fen(fen)
        moves = board.legal_moves

        if uci:
            return [board.uci(move) for move in moves]
        else:
            return [board.san(move) for move in moves]

    def _step(self, tensordict):
        # action
        action = tensordict.get("action")
        board = self.board
        if not self.stateful:
            fen = self._get_fen(tensordict).data
            board.set_fen(fen)
        action = list(board.legal_moves)[action]
        board.push(action)
        self._set_action_space()

        # Collect data
        fen = self.board.fen()
        dest = tensordict.empty()
        hashing = hash(fen)
        dest.set("fen", fen)
        dest.set("hashing", hashing)

        turn = torch.tensor(board.turn)
        if board.is_checkmate():
            # turn flips after every move, even if the game is over
            winner = not turn
            reward_val = 1 if winner == self.lib.WHITE else -1
        else:
            reward_val = 0
        reward = torch.tensor([reward_val], dtype=torch.int32)
        done = self._is_done(board)
        dest.set("reward", reward)
        dest.set("turn", turn)
        dest.set("done", [done])
        dest.set("terminated", [done])
        return dest

    def _set_seed(self, *args, **kwargs):
        ...

    def cardinality(self, tensordict: TensorDictBase | None = None) -> int:
        self._set_action_space(tensordict)
        return self.action_spec.cardinality()
