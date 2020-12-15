from dataclasses import dataclass

import torch

from kalah_python.utils.enums import Action


@dataclass
class ActionInfo:
    logit: torch.Tensor
    prob: torch.Tensor
    critique: torch.Tensor
    action: Action


# hyper parameters for actor-critic
@dataclass
class HyperParams:
    num_episodes: int = 20000
    win_bonus: int = 10
    discount_factor: float = 0.90  # (gamma)
    learning_rate: float = 3e-2  # for optimizer

    def __str__(self) -> str:
        return """
        num_episodes: {},
        win_bonus: {},
        DISCOUNT_FACTOR: {},
        lr: {} 
        """.format(
            self.num_episodes,
            self.win_bonus,
            self.discount_factor,
            self.learning_rate
        )

